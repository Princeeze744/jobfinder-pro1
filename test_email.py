import smtplib
import ssl

try:
    print("🔄 Testing Gmail connection (Port 465)...")
    context = ssl.create_default_context()
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context)
    server.login('trade2uwin@gmail.com', 'vaxvcidhaeydltde')
    print('✅ Connection successful!')
    server.quit()
except Exception as e:
    print(f'❌ Error: {e}')