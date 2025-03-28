import unicodedata
import sqlite3

def normalize_string(input_str):
    """Loại bỏ dấu, lowercase, xóa khoảng trắng"""
    nfkd_str = unicodedata.normalize("NFKD", input_str)
    return "".join([c for c in nfkd_str if not unicodedata.combining(c)]).replace(" ", "").lower()

def get_members_from_db():
    """Lấy danh sách thành viên từ database"""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM members")
    members = {str(row[0]): row[1] for row in cursor.fetchall()}
    conn.close()
    return members
