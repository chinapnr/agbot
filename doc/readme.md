#### jre 问题说明
如果本地无法提供 jre 环境的话，需要注释掉下面代码

    # 声明并初始化签名信息实体类以便获取 RSA 签名对象
    pnr_crypto = encrypt.PnRCrypto()


    # 生成签名信息密文，其生成依赖与本机 JRE 环境，无法提供 JRE 运行环境时需
    # 从被测试环境 Mock 验签信息后执行自动化测试
    params['ChkValue'] = pnr_crypto.sign_by_rsa_for_p2p(
        params['OutCustId'], plain_text, rsa_private_key_file[1])
        
        

#### autogo_ui 运行过程中碰到的问题
运行方式
    
    # 和 autogo 运行方式保持一致，不能借助任何测试框架进行启动
 
依赖包的导入

    # from nose_parameterized import parameterized  =>  pip install parameterized

浏览器驱动

    # autogo_ui 的运行需依赖浏览器驱动，案例中使用的是 chrome