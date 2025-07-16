# pip install flask
import pymysql
from flask import Flask, redirect, url_for, render_template, request, session


app = Flask(__name__)
app.secret_key = 's3cr3t_k3y_1234!@#$'  # 암호화


# MySQL 연결 정보 설정
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'news',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor  # 결과를 딕셔너리 형태로 받기 위함
}


ad_info = {'ad_id' : 'admin', 'ad_pw' : '1234'} # 관리자 아이디 및 비밀번호
category_info = {'politics' : '학생 기사', 'economy' : '경제', 'technology' : '기술'} 
nick = 'Guest'      # 사용자 상태
alert = ''          # 안내 메세지 상태


# 홈페이지로 리디렉션
@app.route('/')
def re_news():
    return redirect(url_for('news'))


# 홈페이지
@app.route('/news')
def news():
    return render_template('news.html', nickname=nick)


# 정치 뉴스
@app.route('/news/politics')
def politics():
    conn = pymysql.connect(**config)
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM posts WHERE category = '학생 기사' ORDER BY created_at DESC")
            posts = cursor.fetchall()
    return render_template('politics.html', posts=posts)


# 경제 뉴스
@app.route('/news/economy')
def economy():
    conn = pymysql.connect(**config)
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM posts WHERE category = '경제' ORDER BY created_at DESC")
            posts = cursor.fetchall()
    return render_template('economy.html', posts=posts)


# 기술 뉴스
@app.route('/news/technology')
def technology():
    conn = pymysql.connect(**config)
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM posts WHERE category = '기술' ORDER BY created_at DESC")
            posts = cursor.fetchall()
    return render_template('technology.html', posts=posts)


@app.route('/news/view', methods=['GET', 'POST'])
def view():
    return select_view()


def select_view():
    post_id = request.args.get('post_id')
    
    conn = pymysql.connect(**config)
    with conn:
        with conn.cursor() as cursor:
            # 조회수 1 증가
            update_sql = "UPDATE posts SET views = views + 1 WHERE post_id = %s"
            cursor.execute(update_sql, (post_id,))
            conn.commit()

            # 해당 게시글 가져오기
            sql = "SELECT * FROM posts WHERE post_id = %s"
            cursor.execute(sql, (post_id,))
            post = cursor.fetchone()

            category = post['category']

            # 키값으로 키 조회
            for key, value in category_info.items():
                if value == category:
                    print(key)
                    break

    if post:
        return render_template('view.html', post=post, category=key)
    else:
        return "게시글을 찾을 수 없습니다.", 404


# # 검색
# @app.route('/news/search', methods=['GET', 'POST'])
# def search():
    


# 글쓰기
@app.route('/news/write', methods=['GET', 'POST'])
def write():
    category = request.args.get('category')
    return render_template('write.html', category=category_info[category])


@app.route('/news/getWrite', methods=['GET', 'POST'])
def getWrite():
    category = request.form.get('category')
    title = request.form.get('title')
    content = request.form.get('content')

    print(category)
    print(title)
    print(content)

    try:
    # 데이터베이스 연결
        conn = pymysql.connect(**config)
    
        with conn:
            with conn.cursor() as cursor:
                # SQL 실행 예: posts 테이블에서 모든 데이터 조회
                sql = "INSERT INTO posts (category, title, content) VALUES (%s, %s, %s)"
                cursor.execute(sql, (category, title, content))
                conn.commit()

                result = cursor.fetchall()
                for row in result:
                    print(row)
        alert = 'write_success'

        # 키값으로 키 조회
        for key, value in category_info.items():
            if value == category:
                print(key)
                break

        return render_template('alert.html', status=alert, category=key)

    except Exception as e:
        alert = 'write_error'
        print("에러 발생:", e)
        return render_template('alert.html', status=alert)



@app.route('/news/modify', methods=['GET', 'POST'])
def modify():
    if request.method == 'GET':
        post_id = request.args.get('post_id')

        try:
            conn = pymysql.connect(**config)
            with conn:
                with conn.cursor() as cursor:
                    sql = "SELECT * FROM posts WHERE post_id = %s"
                    cursor.execute(sql, (post_id,))
                    post = cursor.fetchone()

            if post:
                return render_template('modify.html', post=post)
            else:
                return "게시글을 찾을 수 없습니다.", 404

        except Exception as e:
            print("수정 폼 로딩 중 오류 발생:", e)
            return "게시글 수정 폼을 불러오는 중 오류가 발생했습니다.", 500

    elif request.method == 'POST':
        post_id = request.args.get('post_id')
        title = request.form.get('title')
        content = request.form.get('content')
        category = request.form.get('category')

        try:
            conn = pymysql.connect(**config)
            with conn:
                with conn.cursor() as cursor:
                    sql = """
                    UPDATE posts
                    SET title = %s, content = %s, category = %s
                    WHERE post_id = %s
                    """
                    cursor.execute(sql, (title, content, category, post_id))
                    conn.commit()
            return redirect(url_for('view', post_id=post_id))

        except Exception as e:
            print("수정 중 오류 발생:", e)
            return "게시글 수정 중 오류가 발생했습니다.", 500


@app.route('/news/getModify', methods=['GET', 'POST'])
def getModify():
    post_id = request.form.get('post_id')
    title = request.form.get('title')
    content = request.form.get('content')
    category = request.form.get('category')

    try:
        conn = pymysql.connect(**config)
        with conn:
            with conn.cursor() as cursor:
                sql = """
                    UPDATE posts
                    SET title = %s, content = %s, category = %s
                    WHERE post_id = %s
                """
                cursor.execute(sql, (title, content, category, post_id))
            conn.commit()
        
        alert = 'modify_success'

        # 키값으로 키 조회
        for key, value in category_info.items():
            if value == category:
                print(key)
                break

        return render_template('alert.html', status=alert, category=key, post_id=post_id)

    except Exception as e:
        print("기사 수정 중 오류 발생:", e)
        alert = 'modify_fail'
        return render_template('alert.html', status=alert)



# 기사 삭제
@app.route('/news/delete')
def delete():
    post_id = request.args.get('post_id')

    if not post_id:
        return "삭제할 게시글 ID가 없습니다.", 400

    try:
        conn = pymysql.connect(**config)
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT category FROM posts WHERE post_id = %s", (post_id,))
                post = cursor.fetchone()
                if not post:
                    return "삭제할 게시글을 찾을 수 없습니다.", 404
                
                category = post['category']

                # 게시글 삭제
                cursor.execute("DELETE FROM posts WHERE post_id = %s", (post_id,))
                conn.commit()

        category_key = None
        for key, value in category_info.items():
            if value == category:
                category_key = key
                break
        
        if category_key:
            alert = 'delete_success'
            return render_template('alert.html', status=alert, category=category_key)
        else:
            alert = 'delete_fail'
            return render_template('alert.html', status=alert)

    except Exception as e:
        print("삭제 중 오류 발생:", e)
        return "게시글 삭제 중 오류가 발생했습니다.", 500




# 검색
@app.route('/news/search')
def search():
    keyword = request.args.get('q', '')
    results = []
    no_results = False

    try:
        conn = pymysql.connect(**config)
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
                SELECT post_id, title, created_at, views FROM posts
                WHERE title LIKE %s OR content LIKE %s
                ORDER BY created_at DESC
            """
            like_keyword = f'%{keyword}%'
            cursor.execute(sql, (like_keyword, like_keyword))
            results = cursor.fetchall()

            if not results:
                no_results = True

    except Exception as e:
        print("검색 오류:", e)
        no_results = True  # DB 오류도 결과 없음 처리 가능

    return render_template('news.html', results=results, keyword=keyword, no_results=no_results)



# 관리자 로그인
@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/getLogin', methods=['GET', 'POST'])
def getLogin():

    id = request.form.get('id')
    pw = request.form.get('pw')

    if((id == ad_info['ad_id']) and (pw == ad_info['ad_pw'])):
        session['login_status'] = 1
        return render_template('news.html')
    else:
        alert = 'login_fail'
        return render_template('alert.html', status=alert)


# 관리자 로그아웃
@app.route('/logout')
def logout():
    session['login_status'] = 0
    return render_template('news.html')


if __name__ == '__main__':
    app.run(debug=True)