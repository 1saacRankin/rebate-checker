import subprocess

def send_mac_notification(title: str, message: str):
    try:
        subprocess.run([
            "terminal-notifier",
            "-title", title,
            "-message", message
        ], check=True)
        print("Notification sent successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to send notification: {e}")

if __name__ == "__main__":
    send_mac_notification(
        "🚨 Go Electric Rebates Update",
        "Notice disappeared! Applications may be open."
    )


