import os
import smtplib
from email import encoders  # 导入编码器
from email.mime.base import MIMEBase  # MIME子类的基类
from email.mime.multipart import MIMEMultipart  # 导入MIMEMultipart类
from email.mime.text import MIMEText

from fishbase import logger, fish_file

from agbot.core.model.context import VerticalContext
from agbot.core.utils import is_not_blank
from .context_processor_excel import task_context_processor as task_context_processor_excel


def task_context_processor(vertical_ctx: VerticalContext):
    result_mail_receiver_text = vertical_ctx.task_context.task_model.pass_through.get('result_mail_receiver')
    if not is_not_blank(result_mail_receiver_text):
        return

    task_context_processor_excel(vertical_ctx)

    result_mail_receiver = result_mail_receiver_text.split(',')

    sys_mail_conf = vertical_ctx.sys_conf_dict['system']['ext']['context_processor_mail']

    msg = MIMEMultipart('related')

    mail_matter = """
    <p>Agbot 执行结果</p>
    <p>task_id: {}</p>
    <p>task_src: {}</p>
    <p>{}</p>
    """.format(vertical_ctx.task_context.task_model.id,
               vertical_ctx.task_context.task_model.task_src,
               vertical_ctx.task_context.status.value)
    matter = MIMEText(mail_matter, 'html', 'utf-8')
    msg.attach(matter)

    csv_filename = vertical_ctx.sys_conf_dict.get('excel_context_file_name',
                                                  '{task_id}_result.xlsx') \
        .format(task_id=vertical_ctx.task_context.task_model.id)
    csv_file_path = fish_file.get_abs_filename_with_sub_path('result', csv_filename)[1]
    attachfile = MIMEBase('applocation', 'octet-stream')  # 创建对象指定主要类型和次要类型
    attachfile.set_payload(open(csv_file_path, 'rb').read())  # 将消息内容设置为有效载荷
    attachfile.add_header('Content-Disposition', 'attachment', filename=('utf-8', '', csv_filename))  # 扩展标题设置
    encoders.encode_base64(attachfile)
    msg.attach(attachfile)  # 附加对象加入到msg

    msg['From'] = 'agbot'  # 发送者
    msg['To'] = ','.join(result_mail_receiver)  # 接收者
    msg['Subject'] = 'agbot task result {}'.format(vertical_ctx.task_context.task_model.id)
    try:
        with smtplib.SMTP(host=sys_mail_conf['server']['host'],
                          port=sys_mail_conf['server']['port']) as server:
            server.login(sys_mail_conf['server']['username'], sys_mail_conf['server']['password'])
            server.sendmail('agbot', result_mail_receiver, msg.as_string())
            server.quit()
        logger.info('result mail send success: {} {}'.format(vertical_ctx.task_context.task_model.id,
                                                             ','.join(result_mail_receiver)))
    except Exception as e:
        logger.error('result mail send failure：{} {}'.format(vertical_ctx.task_context.task_model.id,
                                                             str(e)))
    finally:
        if vertical_ctx.sys_conf_dict['system']['ext']['context_processor_excel'].get('enabled') != True:
            os.remove(csv_file_path)
