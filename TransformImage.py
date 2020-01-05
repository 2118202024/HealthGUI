  # -*- encoding: utf-8 -*-
import base64
import pymysql as MySQLdb

def TransformBase64(img_name):
    """
    image -> base64
    :param img_name:
    :return:
    """
    img_path = "./bitmaps/%s.jpg" % img_name
    try:
        with open(img_path, 'rb') as file:
            image_data = file.read()
            base64_data = base64.b64encode(image_data)  # 'bytes'型数据
            str_base64_data = base64_data.decode()#str型数据
            return str_base64_data
    except:
        return "erro"

def UpdateInfoImage(kinfe_name):
    data=TransformBase64(kinfe_name)
    print(data)
    if data != "erro":
        DB = MySQLdb.connect(host="47.101.169.42",port=3306, user="zx", passwd="12345678", db="A_healthy_recipes", charset='utf8')
        cursor = DB.cursor()
        # print("UPDATE `recipe_details` set `picture`='%s' WHERE `recipe_name`='%s'" % (data,kinfe_name))
        cursor.execute(
            "UPDATE `recipe_details` set `picture`='%s' WHERE `recipe_name`='%s'" % (data,'上汤娃娃菜'))
        DB.commit()
        print("success")
    else:
        print("erro2")

def ReadInfoImage(kinfe_name):
    DB = MySQLdb.connect(host="47.101.169.42",port=3306, user="zx", passwd="12345678", db="A_healthy_recipes", charset='utf8')
    cursor = DB.cursor()
    cursor.execute("select `picture`  from `recipe_details` where `recipe_name`='%s'" %(kinfe_name))
    record=cursor.fetchone()
    return record

def ShowImage(kinfe_name):
    """
    base64 -> image
    :return:
    """
    kinfe_name=ReadInfoImage(kinfe_name)
    print(kinfe_name)
    with open('TJDZ_1.jpg', 'wb') as file:
        image = base64.b64decode(kinfe_name[0])  # 解码
        file.write(image)

if __name__ == '__main__':
    # info=ShowImage("清炒虾仁")
    info=UpdateInfoImage("wwc")