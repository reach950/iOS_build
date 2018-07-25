## 使用说明：

**1、添加构建脚本；**

- 将`build_scripts`文件夹及其文件拷贝至目标构建代码库的根目录下；
- 修改pgyer_uploader中的_API_KEY
- 将`build_scripts`提交到项目的仓库中。

**2、安装python3及requests库；**

```bash
$ brew install python3
$ pip3 install requests
```

**3、运行jenkins，安装必备插件(Git plugin,Hudson Post build task)；**

```bash
$ nohup java -jar jenkins_located_path/jenkins.war &
```

**4、创建Jenkins Job；**

- 在Jenkins中创建一个`Freestyle project`类型的Job，先不进行任何配置；
- 然后将`config.xml`文件拷贝到`~/.jenkins/jobs/YourProject/`中覆盖原有配置文件，重启Jenkins；
- 完成配置文件替换和重启后，刚创建好的Job就已完成了大部分配置；
- 在`Job Configure`中根据项目实际情况调整配置，其中`Git Repositories`是必须修改的，其它配置项可选择性地进行调整。

**5、在gitlab项目中添加webhook；**

- webhook地址：http://your-jenkins-server/gitlab/notify_commit
- [说明文档](http://note.youdao.com/groupshare/?token=186C10BBE6DA46A1949DD139EF7EF8B0&gid=209446)

## Read More ...

除了与Jenkins实现持续集成，构建脚本还可单独使用，使用方式如下：

- 构建生成可在模拟器中运行的`.app`文件:

```bash
$ python3 build_scripts/build.py \
    --scheme ${SCHEME} \
    --workspace ${XCWORKSPACE} \
    --sdk iphonesimulator \
    --configuration ${CONFIGURATION} \
    --output_folder ${OUTPUT_FOLDER}
```

- 构建生成可在移动设备中运行的`.ipa`文件，需要在plist文件中设置签名证书:

```bash
$ python3 build_scripts/build.py \
    --scheme ${SCHEME} \
    --workspace ${XCWORKSPACE} \
    --sdk iphoneos \
    --configuration ${CONFIGURATION} \
    --output_folder ${OUTPUT_FOLDER} \
    --export_options_plist_path ${PLIST}
```
