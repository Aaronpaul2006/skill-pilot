from app import create_app

app = create_app()

if __name__ == '__main__':
    print("==============================")
    print("🚀 SKILL PILOT starting...")
    print("📍 Test Panel: http://127.0.0.1:5000/test")
    print("==============================")
    app.run(host='0.0.0.0', port=5000, debug=True)
