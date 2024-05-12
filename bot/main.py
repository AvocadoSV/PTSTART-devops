import logging
import re
import paramiko
import psycopg2

import os
from dotenv import load_dotenv
from telegram.ext import CommandHandler, CallbackContext
import subprocess


from telegram import Update, ForceReply
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)

load_dotenv()
TOKEN = os.getenv("TOKEN")


# Подключаем логирование
logging.basicConfig(
    filename="logfile.txt",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f"Привет {user.full_name}!")


def helpCommand(update: Update, context):
    update.message.reply_text("Help!")


def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text("Введите текст для поиска телефонных номеров: ")

    return "find_phone_number"


def find_phone_number(update, context):
    user_input = update.message.text

    phoneNumRegex = re.compile(
        r"((?:\+7|8)(?:[-\s]?\(?\d{3}\)?[-\s]?)\d{3}[-\s]?\d{2}[-\s]?\d{2})", re.VERBOSE
    )

    phoneNumberList = phoneNumRegex.findall(user_input)

    if not phoneNumberList:
        update.message.reply_text("Телефонные номера не найдены")
        return ConversationHandler.END

    phoneNumbers = ""
    for i, number in enumerate(phoneNumberList, start=1):
        phoneNumbers += f"{i}. {number}\n"

    update.message.reply_text(phoneNumbers)

    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )
        cursor = conn.cursor()

        for number in phoneNumberList:
            try:
                cursor.execute(
                    "INSERT INTO phone_numbers (phone_number) VALUES (%s)", (number,)
                )
                conn.commit()
            except psycopg2.Error as e:
                conn.rollback()
                print("Ошибка при вставке номера телефона:", e)

        cursor.close()
        conn.close()
        update.message.reply_text("Найденные номера успешно записаны в базу данных.")
    except Exception as e:
        print("Ошибка при соединении с базой данных:", e)
        update.message.reply_text("Произошла ошибка при записи номеров в базу данных.")

    return ConversationHandler.END


def find_email_command(update: Update, context):
    update.message.reply_text("Введите текст для поиска email-адресов:")
    return "find_email"


def find_email(update, context):
    user_input = update.message.text

    emailRegex = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

    emailList = emailRegex.findall(user_input)

    if not emailList:
        update.message.reply_text("Email-адреса не найдены")
        return ConversationHandler.END

    emails = ""
    for i, email in enumerate(emailList, start=1):
        emails += f"{i}. {email}\n"

    update.message.reply_text(emails)
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )
        cursor = conn.cursor()

        for email in emailList:
            try:
                cursor.execute("INSERT INTO emails (email) VALUES (%s)", (email,))
                conn.commit()
            except psycopg2.Error as e:
                conn.rollback()
                print("Ошибка при вставке email-адреса:", e)

        cursor.close()
        conn.close()
        update.message.reply_text(
            "Найденные email-адреса успешно записаны в базу данных."
        )
    except Exception as e:
        print("Ошибка при соединении с базой данных:", e)
        update.message.reply_text(
            "Произошла ошибка при записи email-адресов в базу данных."
        )

    return ConversationHandler.END


def verify_password_command(update: Update, context):
    update.message.reply_text("Введите пароль для проверки:")
    return "verify_password"


def verify_password(update: Update, context):
    password = update.message.text
    password_regex = re.compile(
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()])[A-Za-z\d!@#$%^&*()]{8,}$"
    )

    if password_regex.match(password):
        update.message.reply_text("Пароль сложный")
    else:
        update.message.reply_text("Пароль простой")
    return ConversationHandler.END


SSH_HOST = os.getenv("RM_HOST")
SSH_PORT = os.getenv("RM_PORT")
SSH_USERNAME = os.getenv("RM_USER")
SSH_PASSWORD = os.getenv("RM_PASSWORD")


def execute_ssh_command(command):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SSH_HOST, SSH_PORT, SSH_USERNAME, SSH_PASSWORD)
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode("utf-8")
        error = stderr.read().decode("utf-8")
        ssh.close()
        if error:
            return f"Ошибка: {error}"
        return output
    except Exception as e:
        return f"Ошибка: {e}"


def get_release(update: Update, context):
    output = execute_ssh_command("cat /etc/os-release")
    update.message.reply_text(output)


def get_uname(update: Update, context):
    output = execute_ssh_command("uname -a")
    update.message.reply_text(output)


def get_uptime(update: Update, context):
    output = execute_ssh_command("uptime")
    update.message.reply_text(output)


def get_df(update: Update, context):
    output = execute_ssh_command("df")
    update.message.reply_text(output)


def get_free(update: Update, context):
    output = execute_ssh_command("free")
    update.message.reply_text(output)


def get_mpstat(update: Update, context):
    output = execute_ssh_command("mpstat")
    update.message.reply_text(output)


def get_w(update: Update, context):
    output = execute_ssh_command("w")
    update.message.reply_text(output)


def get_ps(update: Update, context):
    output = execute_ssh_command("ps")
    update.message.reply_text(output)


def get_ss(update: Update, context):
    output = execute_ssh_command("ss -lntu")
    update.message.reply_text(output)


def get_auth(update: Update, context):
    output = execute_ssh_command("last -10")
    update.message.reply_text(output)


def get_critical(update: Update, context):
    output = execute_ssh_command("journalctl -p err -b -n 5")
    update.message.reply_text(output)


def get_services(update: Update, context):
    output = execute_ssh_command(
        "systemctl list-unit-files --type=service | head -n 50"
    )
    update.message.reply_text(output)


def get_apt_list(update: Update, context):
    package_name = " ".join(context.args)

    if not package_name:
        output = execute_ssh_command(
            "dpkg --get-selections | grep -v deinstall | head -n 170"
        )
    else:
        output = execute_ssh_command(f"apt-cache show {package_name}")

    update.message.reply_text(output)


def get_replication_logs(update: Update, context: CallbackContext):
    # Параметры SSH-соединения
    SSH_HOST = os.getenv("RM_HOST")
    SSH_PORT = os.getenv("RM_PORT")
    SSH_USERNAME = os.getenv("RM_USER")
    SSH_PASSWORD = os.getenv("RM_PASSWORD")

    log_file_path = "/var/log/postgresql/postgresql-13-main.log"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USERNAME, SSH_PASSWORD)

    stdin, stdout, stderr = ssh.exec_command(
        f"test -f {log_file_path} && echo 'File exists'"
    )
    file_exists = stdout.read().decode("utf-8").strip()

    if not file_exists:
        update.message.reply_text(
            "Файл с логами репликации не найден на мастер-сервере"
        )
        ssh.close()
        return

    stdin, stdout, stderr = ssh.exec_command(f"tail -n 20 {log_file_path}")

    tail_output = stdout.read().decode("utf-8")
    ssh.close()

    update.message.reply_text(tail_output)


def get_emails_command(update: Update, context: CallbackContext):
    update.message.reply_text("Выполняю поиск email-адресов...")
    emails = get_emails_from_database()
    if emails:
        update.message.reply_text("\n".join(emails))
    else:
        update.message.reply_text("Email-адреса не найдены")


def get_phone_numbers_command(update: Update, context: CallbackContext):
    update.message.reply_text("Выполняю поиск номеров телефона...")
    phone_numbers = get_phone_numbers_from_database()
    if phone_numbers:
        update.message.reply_text("\n".join(phone_numbers))
    else:
        update.message.reply_text("Номера телефона не найдены")


def get_emails_from_database():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_REPL_USER"),
            password=os.getenv("DB_REPL_PASSWORD"),
            host=os.getenv("DB_REPL_HOST"),
            port=os.getenv("DB_REPL_PORT"),
        )
        cursor = conn.cursor()

        cursor.execute("SELECT email FROM emails")

        emails = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return emails
    except Exception as e:
        print("Ошибка при получении email-адресов:", e)
        return None


def get_phone_numbers_from_database():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_REPL_USER"),
            password=os.getenv("DB_REPL_PASSWORD"),
            host=os.getenv("DB_REPL_HOST"),
            port=os.getenv("DB_REPL_PORT"),
        )
        cursor = conn.cursor()

        cursor.execute("SELECT phone_number FROM phone_numbers")

        phone_numbers = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return phone_numbers
    except Exception as e:
        print("Ошибка при получении номеров телефона:", e)
        return None


def echo(update: Update, context):
    update.message.reply_text(update.message.text)


def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler("find_phone_number", findPhoneNumbersCommand)],
        states={
            "find_phone_number": [
                MessageHandler(Filters.text & ~Filters.command, find_phone_number)
            ],
        },
        fallbacks=[],
    )
    conv_handler_find_email = ConversationHandler(
        entry_points=[CommandHandler("find_email", find_email_command)],
        states={
            "find_email": [MessageHandler(Filters.text & ~Filters.command, find_email)]
        },
        fallbacks=[],
    )
    conv_handler_verify_password = ConversationHandler(
        entry_points=[CommandHandler("verify_password", verify_password_command)],
        states={
            "verify_password": [
                MessageHandler(Filters.text & ~Filters.command, verify_password)
            ]
        },
        fallbacks=[],
    )

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(conv_handler_find_email)
    dp.add_handler(conv_handler_verify_password)
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_auth", get_auth))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_apt_list", get_apt_list))
    dp.add_handler(CommandHandler("get_repl_logs", get_replication_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails_command))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers_command))

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    main()
