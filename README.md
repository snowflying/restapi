Python RESTful API
==================

A RESTful API Service Framework.

### 1 简介
    一个十分简洁的 RESTful API Service 框架，使用该框架能够快速搭建 RESTful 应用程序。
    该框架支持 Middleware（中间件）、Serialize（序列化)和 Deserialize（反序列化）。

### 2 Pythont版本和第三方信赖库
    webob：            －－－ 实现了Request和Response以及WSGI接口。
    routes             －－－ 实现Mapper和路由。
    eventlet(optional) －－－ 实现了Web Server。
    
    如果不需要eventlet来做 Web Server，则该软件包支持 Python2 和 Python3；否则，只能使用 Python2。
    具体原因请参见 eventlet 库。

### 3 安装
    快速安装：  pip install restapi2
    
    注：PYPI中已经有 RestAPI 软件包，因此安装包命名为 restapi2，但使用时还是用 restapi。

### 4 用法
    在此包中，必须导入使用的只有三个：load_router、Mapper、Controller。

    load_router实现的URL路由，Mapper用来定义一个URL地图，Controller用来定义一个控制器，
    控制器中的方法是与URL对应的动作————处理HTTP请求。

    最简单的使用方法：只需要重载Controller类，并在其中定义一些方法（即Action，动作）；
    然后再用Mapper类定义一个实例，并将一些URL和Controller类中的Action关联起来；接着，
    将该Mapper实例作为参数调用load_router函数（注：load_router的返回值是一个WSGI接口）；
    最后，将load_router的返回值传递给符合WSGI接口Web Server，如Apache或eventlet。
    注：Action的第二个参数必须是一个Request对象，返回值是None、Response对象、一个字符串
    或字符串列表。

    例子：

    from restapi import load_router, Mapper, Controller
    from eventlet

    class HelloController(Controller):
        def hello(self, request, name):
            return "Hello, %s" % name

    def get_mapper():
        mapper = Mapper()
        hellocontroller = Hellocontroller()
        mapper.connect('hello', '/hello/{name}'
                       controller=hellocontroller,
                       action='hello',
                       conditions={'method': ['GET']})
        return mapper

    if __name__ == "__main__":
        host = '0.0.0.0'
        port = 8080
        mapper = get_mapper()
        app = load_router(mapper)
        eventlet.wsgi.server((host, port), app)

    说明：上面的代码即实现了一个RESTfull接口的Web服务，并监听在当前系统中的所有IP地址的
    8080端口上。

    在本机中，通过任何一个HTTP客户端访问http://127.0.0.1:8080/hello/restapi，将会得到
    “Hello, restapi”。

    当Action返回一个字符串或字符串列表时，HTTP客户端得到的HTTP状态码是200。当希望返回的
    HTTP状态码不是200时，也可以返回一个Response对象————指定了相应的状态码。

    在restapi.responses模块中，定义了各个对应状态码的Response类型，只需要返回相应的类型
    的一个实例即可，另外，可以把响应体的内容作为参数传递给这些Response类型。
    注：这些Response类型和webob.Response类型的接口一模一样。

    如果响应体为空，也可以抛出一个异常。在restapi.exceptions模块中，定义对应各个状态码的
    异常类型，只需要在Action中抛出相应的异常，restapi就会捕获它并返回相应的状态码。其他
    的异常会被认为是 400 异常，即返回 400 状态码。

### 5 中间件（Middleware）
    Restapi包支持 Middleware。

    在restapi.middlewares模块中，有 Middleware类型接口，只需要继承它，并重载
    process_request和process_response方法即可；前者处理Request请求，后者处理Response响应。
    然后使用 register_middleware 函数将此派生类注册到restapi包当中即可。
    注：也可以使用 register_middlewares 函数注册多个中间件。

    注：如果process_request的返回值不为None，说明HTTP请求已经在中间件中处理了了，它的返回
    值会直接作为Action的返回值直接返回，不会经过Action和process_response。

### 6 序列化（Serializer）和反序列化（Deserializer）
    Restapi包也支持 Serializer 和 Deserializer。

    Serializer的返回值的Action的返回值一样，Deserializer的返回值必须是个字典。

    在restapi中有个Serializer类型原型，其中有两个方法：serializer和deserializer，分别做
    序列化和反序列化。序列化是将Action的返回值（可能是字典等Python对象）转换成HTTP协议
    格式，比如：Action的返回值是个Python中一个文件对象，序列化就是把这个对象的属性转换成
    HTTP响应头，将文件对象的内容（即文件的内容）转换成响应体。反序列化是将HTTP请求内容
    转换成一个Python对象，一般来说，反序列化是序列化的逆运算。

    可以继承Serializer类型，并重载serializer和deserializer方法。

    注意：当使用了Serializer时，必须用Resource类型包装Controller实例，并用Serializer派生类
    的实例作为第二个参数传递给Resource，比如：如果派生一个JSONSerializer，那么，上面例子的
    Controller写法应该是：hellocontroller = Resource(Controller(), JSONSerializer())。

    说明：如果有多个序列化实例，可以将其组成一个元组或列表，然后作为第二个参数传递给Resource，
    Resource会按照它们的顺序依次处理。

    Restapi也在serializers模块中定义了一些简单的序列化类：NoSerializer 和 JSONSerializer。
    其中，Noserializer不做任何操作，原样返回。JSONSerializer对于序列化，将Action的结果序列化
    成JSON格式的字节型的字符串并返回；对于反序列化，将Request的请求体反序列化成一个字典并返回。

### 7 简单的Server
    Restapi包实现了一个简单的Server————通过eventlet.wsgi.server实现的，位于restapi.main模块中。

    main模块只有一个函数：start_server。

    start_server(mapper, addr, pid_file=None, daemon=False, server=None)
    start_server启动 RESTful API Server，直到Server结束才返回。其中:
        mapper是Mapper实例；
        addr是一个元组或列表，第一个元素是监听的主机IP地址（如：'0.0.0.0'），第二个是监听的端口（如：8080）
        pid_file是一个表示一个文件绝对路径的字符串，它用来记录程序的PID值。
        daemon表示该服务是否以Daemon形式启动。
        server是一个自定义的HTTP Server服务器，如：Apache，默认使用eventlet.wsgi.server。
    注：（1）server参数必须 WSGI 接口的，如：如果使用Apache，则可能需要使用wsgi_mod模块。
        （2）eventlet中的server使用的是协程，它会自动对临界资源做同步，也就是说，不需要用户
             自己对临界资源进行同步。由于协程的原因，在action中处理请求时，不能占用太长的时间，
             尤其是阻塞，否则其他的请求无法响应；对于需要长时间处理的请求，可以放入一个线程中
             去响应。但start_server已经对os、socket、time等标准库打过patch，因此，这些标准库
             中的阻塞函数可以正常使用，如：time.sleep。
             如果使用了自定义Server，那么，对于各个请求间的临界资源的同步需要由用户自己来完成。
             Python的标准库中已经提供了线程锁和进程锁。
        （3）start_server不会抛出任何异常。

### 8 样例
    见examples目录。

