# 贡献指南

## 代码贡献的一般流程

以下内容在于帮助大家迅速理解如何完成自己的工作并将代码贡献到项目中，请灵活使用Google或百度进一步理清不明白的部分。

### 写在贡献之前
 
当大家加入私有仓库后，大家应当能够通过git将项目克隆到本地，并将项目运行起来，这里仍然推荐大家使用docker完成相关项目的运行。此外，在生产环境中，使用原生pip和poetry是存在风险的。

使用IDE自带的git工具往往就足够了，例如VSCode，Pycharm，Intellij IDEA等，都有便捷的源代码管理，进行分支切换创建，以及提交等操作，乃至是将文件添加至.gitignore都是可以通过相应的源代码管理工具完成的。

### 分支控制和代码提交

因为项目成员众多以及避免分支混乱和僵尸分支问题，这里我们只维护两个分支，main以及dev。前者是主分支，分支节点均具备发行能力；后者是发开分支，日常开发的分支，允许频繁更新。

下面我说明使用git将自己的代码贡献到dev分支的方法。

1) 通过本地创建feat分支的方式完成开发需求

假设你现在需要基于任务增加一个功能，首先将项目分支与远端仓库同步（`git pull/gti fetch`，后者只将本地的远端仓库同步），随后基于`dev`分支创建一个新的分支（`git branch -c dev feat-parser-handler`）并切换到新建分支上（`git checkout feat-parser-handler`）。

这里的`feat-parser-handler`的分支名不作强制要求，可以是你姓名的缩写，如`HXL`，也可以是`feat+功能名称`，feat即feature，这里推荐后者。

先将本地仓库与远端同步是必要操作，因为这样能够尽可能保证你基于最新的代码进行修改。

事实上你可以直接在dev分支上修改，随后创建新的分支，这是基于工作区与分支的独立。

2) 将完成的feat分支推到远端，并提pull request

如果在你完成自己的代码的过程中dev分支又被更新了，这时一种解决方式是将你的新建分支rebase到新的dev分支上（可以基于`git stash/git stash pop`来保存你的更改）。

完成代码开发和本地测试后，你可以将完成的feat分支推送到远端仓库，并通过pull requst要求dev分支merge你的feat分支，这里大家可以简单的说明自己的工作内容。

在reviewer将你的feat分支合并到dev分支后，你的任务就完成了，在github远端仓库的feat分支会被自动删除，你可以相应删除本地的feat分支，当你后续还需要进行开发时依据最新的dev分支创建feat分支。

### 关于本项目的一些开发建议

一般的功能实现，建议大家依据功能的具体实现在`document_generation/handlers`目录下创建py文件，这里我们叫它为`parse_template_handler.py`。

这里举一个例子方便大家理解，大家把握思想即可。

`parse_template`会调用`data_plane`对象的方法，我就叫这个方法为`data_plane.parse_template`，来完成具体的业务逻辑，那么在`document_generation/rest/endpoints.py`的`parse_template`的方法中，除了完成VO的封装（VO即表现层对象，可以理解为REST请求的输入和输出，而一般的函数和方法的输入输出不认为是VO），那就是调用`data_plane.parse_template`来完成具体业务逻辑。

为了便于协同工作，这里建议大家仅在`document_generation/handlers/dataplane.py`的对应方法中，在这个例子中是`data_plane.parse_template`，调用实际具体完成相应业务逻辑的对象方法，也就是我们创建的`parse_template_handler.py`中的具体方法，如`parse_template_handler.handle`。

大家完成业务逻辑一般都会涉及其他模块，请记得管理依赖。

此外，对于各种IDE的配置以及其他临时文件，大家都可以加入到.gitignore中。