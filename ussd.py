from flask import Flask, request
import pymysql

app = Flask(__name__)

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        db='ussd_appeal_system',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/ussd', methods=['POST'])
def ussd():
    session_id = request.form.get("sessionId")
    service_code = request.form.get("serviceCode")
    phone_number = request.form.get("phoneNumber")
    text = request.form.get("text", "")

    response = ""
    inputs = text.strip().split("*")

    # MAIN MENU
    if text == "":
        response = "CON Welcome to the Marks Appeal System\n"
        response += "1. Check my marks\n"
        response += "2. Appeal my marks\n"
        response += "3. Check appeal status\n"
        response += "4. Exit"

    # CHECK MARKS
    elif inputs[0] == "1":
        if len(inputs) == 1:
            response = "CON Enter your Student ID:"
        elif len(inputs) == 2:
            student_id = inputs[1].upper()
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
                student = cursor.fetchone()
                if not student:
                    response = "END Error: Student ID not found."
                else:
                    cursor.execute("SELECT module_name, mark FROM marks WHERE student_id = %s", (student_id,))
                    marks = cursor.fetchall()
                    if marks:
                        response = "END Your Marks:\n"
                        for m in marks:
                            response += f"{m['module_name']}: {m['mark']}\n"
                    else:
                        response = "END No marks found."
            conn.close()

    # APPEAL MARKS
    elif inputs[0] == "2":
        if len(inputs) == 1:
            response = "CON Enter your Student ID:"
        elif len(inputs) == 2:
            student_id = inputs[1].upper()
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT module_name, mark FROM marks WHERE student_id = %s", (student_id,))
                modules = cursor.fetchall()
                if not modules:
                    response = "END No modules found for student."
                else:
                    menu = "\n".join([f"{i+1}. {m['module_name']} ({m['mark']})" for i, m in enumerate(modules)])
                    response = f"CON Select module to appeal:\n{menu}"
                    response += f"\n0. Go Back"
            conn.close()

        elif len(inputs) == 3:
            selected_index = int(inputs[2]) - 1
            student_id = inputs[1].upper()
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT module_name FROM marks WHERE student_id = %s", (student_id,))
                modules = cursor.fetchall()
                if selected_index < 0 or selected_index >= len(modules):
                    response = "END Invalid selection."
                else:
                    selected_module = modules[selected_index]['module_name']
                    response = f"CON Enter reason for appealing {selected_module}:"
                    response += f"*{selected_module}"
            conn.close()

        elif len(inputs) == 4:
            student_id = inputs[1].upper()
            module_name = inputs[3]
            reason = inputs[2]
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO appeals (student_id, module_name, reason, status)
                    VALUES (%s, %s, %s, %s)
                """, (student_id, module_name, reason, "Pending"))
                conn.commit()
                response = "END Appeal submitted successfully. You will be notified soon."
            conn.close()

    # CHECK APPEAL STATUS
    elif inputs[0] == "3":
        if len(inputs) == 1:
            response = "CON Enter your Student ID:"
        elif len(inputs) == 2:
            student_id = inputs[1].upper()
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT module_name, status
                    FROM appeals
                    WHERE student_id = %s
                """, (student_id,))
                appeals = cursor.fetchall()
                if appeals:
                    response = "END Appeal Status:\n"
                    for a in appeals:
                        response += f"{a['module_name']}: {a['status']}\n"
                else:
                    response = "END No appeals found for this student."
            conn.close()

    elif inputs[0] == "4":
        response = "END Thank you for using the system."

    else:
        response = "END Invalid choice. Please try again."

    return response, 200, {"Content-Type": "text/plain"}

if __name__ == '__main__':
    app.run(port=5000)