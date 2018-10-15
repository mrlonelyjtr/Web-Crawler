## Cookie池  

[![ily4AS.md.png](https://s1.ax1x.com/2018/09/29/ily4AS.md.png)](https://imgchr.com/i/ily4AS)  

### 存储模块

负责存储每个账号的用户名密码以及每个账号对应的Cookies信息，同时还需要提供一些方法来实现方便的存取操作。

### 生成模块

负责生成新的Cookies。此模块会从存储模块逐个拿取账号的用户名和密码，然后模拟登录目标页面，判断登录成功，就将Cookies返回并交给存储模块存储。

### 检测模块

需要定时检测数据库中的Cookies。逐个拿取账号对应的Cookies去请求链接，如果返回的状态是有效的，那么此Cookies没有失效，否则Cookies失效并移除。接下来等待生成模块重新生成即可。

### 接口模块

需要用API来提供对外服务的接口。由于可用的Cookies可能有多个，可以随机返回Cookies的接口，这样保证每个Cookies都有可能被取到。Cookies越多，每个Cookies被取到的概率就会越小，从而减少被封号的风险。