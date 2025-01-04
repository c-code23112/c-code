from flask import Flask, make_response,send_from_directory,render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import hashlib,json
from sqlalchemy.dialects import mysql
from sqlalchemy import create_engine
from sqlalchemy import text

app = Flask(__name__)


app.secret_key = 'your_secret_key'


app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://root:123456@localhost/course_design_system'
app.config['SQLALCHchemy_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])



# 首页，用于选择登录身份
@app.route('/')
def index():
    return render_template('base.html')


# 学生登录
@app.route('/student/login', methods=['POST'])
def student_login():
    student_id = request.form['student_id']
    password = request.form['student_password']

    cur = engine.raw_connection().cursor()
    cur.execute("SELECT * FROM students WHERE student_id=%s AND student_password=%s", (student_id, password))
    student = cur.fetchone()
    cur.close()

    if student:
        session['user_type'] ='student'
        session['user_id'] = student_id
        session['student_name'] = student[1]
        return redirect(url_for('student_index'))
    else:
        return "学生登录失败，请检查学号和密码。"


# 教师登录
@app.route('/teacher/login', methods=['POST'])
def teacher_login():
    teacher_id = request.form['teacher_id']
    password = request.form['teacher_password']

    cur = engine.raw_connection().cursor()
    cur.execute("SELECT * FROM teachers WHERE teacher_id=%s AND teacher_password=%s", (teacher_id, password))
    teacher = cur.fetchone()
    cur.close()

    if teacher:
        session['user_type'] = 'teacher'
        session['user_id'] = teacher_id
        session['teacher_name'] = teacher[1]
        return redirect(url_for('teacher_index'))
    else:
        return "教师登录失败，请检查工资号和密码。"


# 客户登录
@app.route('/customer/login', methods=['POST'])
def customer_login():
    customer_id = request.form['customer_id']
    password = request.form['customer_password']

    cur = engine.raw_connection().cursor()
    cur.execute("SELECT * FROM customers WHERE customer_id=%s AND customer_password=%s", (customer_id, password))
    customer = cur.fetchone()
    cur.close()

    if customer:
        session['user_type'] = 'customer'
        session['user_id'] = customer_id
        return redirect(url_for('customer_index'))
    else:
        return "客户登录失败，请检查账号和密码。"


# 学生主页
@app.route('/student')
def student_index():
    if 'user_type' in session and session['user_type'] =='student':
        return render_template('student/index.html')
    else:
        return redirect(url_for('index'))


# 教师主页
@app.route('/teacher')
def teacher_index():
    if 'user_type' in session and session['user_type'] == 'teacher':
        return render_template('teacher/index.html')
    else:
        return redirect(url_for('index'))


# 客户主页
@app.route('/customer')
def customer_index():
    if 'user_type' in session and session['user_type'] == 'customer':
        return render_template('customer/index.html')
    else:
        return redirect(url_for('index'))

@app.route('/student/topic_selection', methods=['get','POST'])
def topic_selection():
    # 从数据库中获取所有的课程设计题目信息
        cur = engine.raw_connection().cursor()
        cur.execute("SELECT topic_id, topic_name FROM topics")
        raw_topics = cur.fetchall()
    # 将元组列表转换为字典列表
        topics = []
        for topic in raw_topics:
           topics.append({
           "topic_id": topic[0],
           "topic_name": topic[1]})
        cur.close()
        return (render_template('student/topic_selection.html', topics=topics))


# 学生选题功能
@app.route('/student/student_topic_selection', methods=['POST'])
def student_topic_selection():
        student_id = session['user_id']
        topic_id = request.form['topic_id']
        group_members = request.form['group_members']

        cur = engine.raw_connection().cursor()
        # 先查询topics表，检查topic_id是否存在
        cur.execute("SELECT topic_id FROM topics WHERE topic_id = %s", (topic_id,))
        result = cur.fetchone()

        if result:
            # 如果topic_id存在，执行插入操作
            cur.execute(
                "INSERT INTO student_topics (student_id, topic_id, group_members,student_topic_id,is_selected) VALUES (%s, %s, %s,%s,%s)",
                (student_id, topic_id, group_members, None, True))
            engine.raw_connection().commit()
        else:
            print(f"topic_id {topic_id} 不存在于topics表中，请检查！")
        cur.close()
        return "选题成功！等待确认。"

@app.route('/student/s_password_change', methods=['get','POST'])
def s_password_change():
    return render_template('student/password_change.html')
# 学生密码修改功能
@app.route('/student/password_change', methods=['POST'])
def student_password_change():
    if 'user_type' in session and session['user_type'] == 'student':
        student_id = session['user_id']
        old_password = request.form['old_password']
        new_password = request.form['new_password']

        cur = engine.raw_connection().cursor()
        cur.execute("SELECT student_password FROM students WHERE student_id=%s", (student_id,))
        stored_password = cur.fetchone()[0]
        cur.close()

        if stored_password == old_password:
            hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
            cur = engine.raw_connection().cursor()
            cur.execute("UPDATE students SET student_password=%s WHERE student_id=%s", (hashed_new_password, student_id,))
            engine.raw_connection().commit()
            cur.close()
            return "密码修改成功！"
        else:
            return "原密码错误，请重新输入。"
    else:
        return redirect(url_for('index'))

@app.route('/student/s_topic_query', methods=['get','POST'])
def s_topic_query():
    return render_template('student/topic_query.html')

# 学生选题情况查询功能
@app.route('/student/topic_query', methods=['POST'])
def student_topic_query():
    if 'user_type' in session and session['user_type'] == 'student':
        query_type = request.form['query_type']
        query_value = request.form['query_value']

        session_obj = engine.raw_connection().cursor()

        try:
            if query_type == 'by_topic_id':
                query = text("""
                    SELECT st.student_topic_id, t.topic_name, st.student_id, s.student_name, st.group_members, st.is_selected, st.progress_status, st.progress_details
                    FROM student_topics st
                    JOIN topics t ON st.topic_id = t.topic_id
                    JOIN students s ON st.student_id = s.student_id
                    WHERE st.student_topic_id = :query_value
                """)
                results = session_obj.execute(query, {'query_value': query_value}).fetchall()
            elif query_type == 'by_student_id':
                query = text("""
                    SELECT st.student_topic_id, t.topic_name, st.student_id, s.student_name, st.group_members, st.is_selected, st.progress_status, st.progress_details
                    FROM student_topics st
                    JOIN topics t ON st.topic_id = t.topic_id
                    JOIN students s ON st.student_id = s.student_id
                    WHERE st.student_id = :query_value
                """)
                results = session_obj.execute(query, {'query_value': query_value}).fetchall()

            query_results = []
            for row in results:
                result_dict = {
                    'student_topic_id': row[0],
                    'topic_name': row[1],
                    'student_id': row[2],
                    'student_name': row[3],
                    'group_members': row[4],
                    'is_selected': row[5],
                    'progress_status': row[6],
                    'progress_details': row[7]
                }
                query_results.append(result_dict)

            session_obj.close()

            return render_template('student/topic_query.html', query_results=query_results)
        except Exception as e:
            print(f"查询学生课题信息时出现错误：{e}")
            session_obj.close()
            return render_template('student/topic_query.html', query_results=[])
    else:
        return redirect(url_for('index'))

@app.route('/student/s_score_query', methods=['get','POST'])
def s_score_query():
    return render_template('student/score_query.html')
# 学生成绩查询功能
@app.route('/student/score_query')
def student_score_query():
    if 'user_type' in session and session['user_type'] =='student':
        student_id = session['user_id']

        cur = mysql.connection.cursor()
        cur.execute("SELECT score FROM student_scores WHERE student_id=%s", (student_id))
        result = cur.fetchone()
        cur.close()

        if result:
            score = result[0]
            return f"你的课程设计成绩是：{score}"
        else:
            return "成绩尚未公布，请耐心等待。"
    else:
        return redirect(url_for('index'))

@app.route('/student/s_report_upload', methods=['get','POST'])
def s_report_upload():
    return render_template('student/report_upload.html')
# 学生报告上传功能
@app.route('/student/report_upload', methods=['POST'])
def student_report_upload():
    if 'user_type' in session and session['user_type'] =='student':
        student_id = session['user_id']
        report_file = request.files['report_file']

        file_path = f"reports/{student_id}_{report_file.filename}"
        report_file.save(file_path)

        cur = engine.raw_connection().cursor()
        cur.execute("INSERT INTO student_reports (student_id, report_file) VALUES (%s, %s)", (student_id, file_path))
        engine.raw_connection().commit()
        cur.close()

        return "报告上传成功！"
    else:
        return redirect(url_for('index'))


# 教师选题情况查看功能
@app.route('/teacher/topic_view')
def teacher_topic_view():
    if 'user_type' in session and session['user_type'] == 'teacher':
        teacher_id = session['user_id']

        cur = engine.raw_connection().cursor()
        cur.execute("SELECT students.student_name, topics.topic_name, student_topics.group_members FROM student_topics JOIN students ON student_topics.student_id = students.student_id JOIN topics ON student_topics.topic_id = topics.topic_id WHERE topics.teacher_id = %s", (teacher_id))
        results = cur.fetchall()
        cur.close()

        return render_template('teacher/topic_view.html', results=results)
    else:
        return redirect(url_for('index'))

@app.route('/teacher/t_progress_fill', methods=['get','POST'])
def t_progress_fill():
    return render_template('teacher/progress_fill.html')
#学生项目进度
@app.route('/teacher/teacher_progress_fill', methods=['POST'])
def teacher_progress_fill():
    if 'user_type' in session and session['user_type'] == 'teacher':
        teacher_id = session['user_id']

        # 获取前端传来的学生课题进度相关信息
        student_topic_id = request.form['student_topic_id']
        progress_status = request.form['progress_status']
        progress_details = request.form['progress_details']

        # 将进度详情（如果是列表等复杂结构）转换为可存储在数据库中的格式，这里假设转换为JSON字符串
        if isinstance(progress_details, list):
            progress_details_str = json.dumps(progress_details)
        else:
            progress_details_str = progress_details

        cur = engine.raw_connection().cursor()

        try:
            # 先检查该学生课题是否存在
            cur.execute("SELECT * FROM student_topics WHERE student_topic_id=%s", (student_topic_id,))
            if cur.fetchone() is None:
                return "指定的学生课题不存在，请检查！"

            # 更新学生课题进度信息
            cur.execute("UPDATE student_topics SET progress_status=%s, progress_details=%s WHERE student_topic_id=%s",
                        (progress_status, progress_details_str, student_topic_id))
            engine.raw_connection().commit()
            cur.close()

            return "学生课题进度信息更新成功！"
        except Exception as e:
            print(f"更新学生课题进度信息时出现错误：{e}")
            cur.close()
            return "更新学生课题进度信息失败，请稍后再试。"
    else:
        return redirect(url_for('index'))

# 教师报告查看与进度填写功能
@app.route('/teacher/report_view')
def teacher_report_view():
    if 'user_type' in session and session['user_type'] == 'teacher':
        teacher_id = session['user_id']

        cur = mysql.connection.cursor()
        cur.execute("SELECT students.student_name, student_reports.report_file FROM student_reports JOIN students ON student_reports.student_id = students.student_id WHERE students.student_id IN (SELECT student_id FROM student_topics WHERE topic_id IN (SELECT topic_id FROM topics WHERE teacher_id = %s))", (teacher_id))
        results = cur.fetchall()
        cur.close()

        return render_template('teacher/report_view.html', results=results)
    else:
        return redirect(url_for('index'))

@app.route('/teacher/t_score_give', methods=['get','POST'])
def t_score_give():
    return render_template('teacher/score_give.html')
# 教师成绩评定功能
@app.route('/teacher/score_give', methods=['POST'])
def teacher_score_give():
    if 'user_type' in session and session['user_type'] == 'teacher':
        teacher_id = session['user_id']
        student_id = request.form['student_id']
        score = request.form['score']

        cur = engine.raw_connection().cursor()
        cur.execute("INSERT INTO student_scores (teacher_id, student_id, score) VALUES (%s, %s, %s)",
                    (teacher_id, student_id, score))
        engine.raw_connection().commit()
        cur.close()

        return "成绩评定成功！"
    else:
        return redirect(url_for('index'))

@app.route('/teacher/t_password_change', methods=['get','POST'])
def t_password_change():
    return render_template('teacher/password_change.html')
# 教师密码修改功能
@app.route('/teacher/password_change', methods=['POST'])
def teacher_password_change():
    if 'user_type' in session and session['user_type'] == 'teacher':
        teacher_id = session['user_id']
        old_password = request.form['old_password']
        new_password = request.form['new_password']

        cur = engine.raw_connection().cursor()
        cur.execute("SELECT password FROM teachers WHERE teacher_id=%s", (teacher_id))
        stored_password = cur.fetchone()[0]
        cur.close()

        if stored_password == old_password:
            hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
            cur = mysql.connection.cursor()
            cur.execute("UPDATE teachers SET password=%s WHERE teacher_id=%s", (hashed_new_password, teacher_id))
            engine.raw_connection().commit()
            cur.close()
            return "密码修改成功！"
        else:
            return "原密码错误，请重新输入。"
    else:
        return redirect(url_for('index'))
# 教师资料查看功能
@app.route('/teacher/material_view')
def teacher_material_view():
    if 'user_type' in session and session['user_type'] == 'teacher':
        teacher_id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT material_name, material_file FROM learning_material WHERE teacher_id=%s", (teacher_id))

# 教师资料上传功能
@app.route('/teacher/material_upload', methods=['POST'])
def teacher_material_upload():
    if 'user_type' in session and session['user_type'] == 'teacher':
        teacher_id = session['user_id']
        material_file = request.files['material_file']
        material_name = request.form['material_name']

        file_path = f"materials/{teacher_id}_{material_name}_{material_file.filename}"
        material_file.save(file_path)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO learning_materials (teacher_id, material_name, material_file) VALUES (%s, %s, %s)",
                    (teacher_id, material_name, file_path))
        mysql.connection.commit()
        cur.close()

        return "资料上传成功！"
    else:
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)