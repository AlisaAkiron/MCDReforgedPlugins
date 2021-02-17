# Notice

一个简单易用的公告插件
第一次加载会生产默认配置文件，路径为 ***config/notice***

## 依赖项

### 插件依赖
* [mcdreforged]() >= 1.0.0
* [online_player_api](https://github.com/zhang-anzhi/MCDReforgedPlugins/tree/master/OnlinePlayerAPI) = *

## 功能

* 通过指令或者配置文件设置公告标题和内容（最终输出为 ***标题：内容*** 的格式）
* 通过指令或者配置文件删除公告
* 通过指令或者配置文件设置公告框大标题
* 通过指令或者配置文件开启或关闭玩家进入服务器时自动发送的功能
* 通过指令向全服在线玩家广播公告

## 指令

| 指令 | 作用 |
| - | - |
| !!notice | 显示公告 |
| !!notice help | 显示帮助 |
| !!notice add &lt;title&gt; &lt;content&gt; | 添加一条公告 |
| !!notice del &lt;title&gt; | 删除一条公告 |
| !!notice setheader &lt;header&gt; | 修改标题 |
| !!notice autosend &lt;True/False&gt; | 是否在玩家加入服务器时自动发送 |
| !!notice reload | 重载公告和配置文件（直接修改配置文件请用这条指令重载） |
| !!notice broadcast | 向所有在服务器内的玩家广播 |

注1：title, header和content必须用引号括起，引号内可使用转义字符

注2：建议配合 [JoinMOTDR](https://github.com/Van-Involution/JoinMOTDR) 插件使用

## 输出样例

============== &lt;header&gt; ==============

&lt;title1&gt;：&lt;content1&gt;

&lt;title2&gt;：&lt;content2&gt;

&lt;title3&gt;：&lt;content3&gt;

## 其他插件获取信息

如果你的插件需要配合Notice使用来获取公告信息，可通过如下代码获取：

``` python
server.get_plugin_instance('notice').get_notice_rtext();
```

返回值为一个RTextList

例：

``` python
def get_notice(server: ServerInterface, plugin_id: str = 'notice'):
    try:
        return server.get_plugin_instance(plugin_id).get_notice_rtext();
    except Exception:
        warning = RText(f'§cFailed to get instance from plugin "§l{plugin_id}§r"');
        server.logger.warning(warning.to_plain_text())
        return RTextList(warning, '\n')
```