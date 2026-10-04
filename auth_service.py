import requests
import streamlit as st

def get_firebase_api_key():
    return st.secrets.get("FIREBASE_API_KEY", "")

def sign_in_with_email_and_password(email, password):
    """ เข้าสู่ระบบด้วย Email และ Password """
    api_key = get_firebase_api_key()
    if not api_key:
        return {"success": False, "error": "กรุณาตั้งค่า FIREBASE_API_KEY ใน Secrets"}

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        res_data = response.json()
        
        if response.status_code == 200:
            return {"success": True, "info": res_data}
        else:
            error_code = res_data.get("error", {}).get("message", "LOGIN_FAILED")
            return {"success": False, "error": translate_firebase_error(error_code)}
    except Exception as e:
        return {"success": False, "error": f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}"}

def sign_up_with_email_and_password(email, password):
    """ สมัครสมาชิกใหม่ด้วย Email และ Password """
    api_key = get_firebase_api_key()
    if not api_key:
        return {"success": False, "error": "กรุณาตั้งค่า FIREBASE_API_KEY ใน Secrets"}

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        res_data = response.json()
        
        if response.status_code == 200:
            return {"success": True, "info": res_data}
        else:
            error_code = res_data.get("error", {}).get("message", "SIGNUP_FAILED")
            return {"success": False, "error": translate_firebase_error(error_code)}
    except Exception as e:
        return {"success": False, "error": f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}"}

def reset_password(email):
    """ ส่งอีเมลรีเซ็ตรหัสผ่าน """
    api_key = get_firebase_api_key()
    if not api_key:
        return {"success": False, "error": "กรุณาตั้งค่า FIREBASE_API_KEY ใน Secrets"}

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"
    payload = {
        "requestType": "PASSWORD_RESET",
        "email": email
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        res_data = response.json()
        if response.status_code == 200:
            return {"success": True}
        else:
            error_code = res_data.get("error", {}).get("message", "RESET_FAILED")
            return {"success": False, "error": translate_firebase_error(error_code)}
    except Exception as e:
        return {"success": False, "error": f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}"}

def translate_firebase_error(error_code):
    """ แปลง Error Code จาก Firebase เป็นภาษาไทย """
    errors = {
        "EMAIL_EXISTS": "อีเมลนี้ถูกใช้งานในระบบแล้ว",
        "INVALID_EMAIL": "รูปแบบอีเมลไม่ถูกต้อง",
        "WEAK_PASSWORD : Thread1": "รหัสผ่านต้องมีความยาวอย่างน้อย 6 ตัวอักษร",
        "WEAK_PASSWORD": "รหัสผ่านง่ายเกินไป (ต้องมีอย่างน้อย 6 ตัวอักษร)",
        "EMAIL_NOT_FOUND": "ไม่พบบัญชีผู้ใช้นี้ในระบบ",
        "INVALID_PASSWORD": "รหัสผ่านไม่ถูกต้อง",
        "INVALID_LOGIN_CREDENTIALS": "อีเมลหรือรหัสผ่านไม่ถูกต้อง",
        "USER_DISABLED": "บัญชีนี้ถูกระงับการใช้งาน",
        "TOO_MANY_ATTEMPTS_TRY_LATER": "พยายามเข้าสู่ระบบถี่เกินไป โปรดลองใหม่ภายหลัง"
    }
    return errors.get(error_code, f"เกิดข้อผิดพลาด: {error_code}")