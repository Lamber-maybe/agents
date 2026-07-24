---
title: Docker镜像优化
date: 2026-07-20
---

随着容器技术的普及，越来越多的团队开始使用Docker来部署应用。但是在实际使用过程中，很多人会发现镜像变得越来越大，这会带来很多问题。本文将探讨一些优化方法。

镜像大的原因有很多。首先是基础镜像选得太大，比如很多人直接用ubuntu或者node的默认镜像，这些镜像本身就有几百MB甚至上GB。其次是构建过程中把不需要的东西打进去了，比如编译工具链、测试文件、文档等等。还有就是层的问题，Docker镜像是分层的，如果你在一层里下载了一个大文件然后在另一层里删除它，实际上镜像体积并不会变小，因为那个文件还在之前的层里。另外node_modules、apt缓存、pip缓存这些也经常被不小心打进镜像。

我们项目原来的Go服务镜像是1.2GB，经过优化后降到了180MB，下面说说具体做法。

多阶段构建是最有效的手段。它的思路是用一个镜像做构建，再把产物拷贝到一个干净的运行镜像里。这样编译器、依赖包这些构建期需要的东西就完全不会出现在最终镜像里。

```dockerfile
FROM golang:1.24 AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 go build -o server .

FROM alpine:3.20
COPY --from=builder /app/server /server
ENTRYPOINT ["/server"]
```

这一步做完我们的镜像就从1.2GB降到了320MB左右。

然后是基础镜像的选择。alpine是最常用的小镜像，只有5MB左右。不过alpine用的是musl libc，有些依赖glibc的程序会有兼容性问题，尤其是一些Python的native扩展。google的distroless是另一个选择，它连shell和包管理器都没有，安全性更好，调试起来麻烦一些。对于Go这种可以静态编译的语言，甚至可以用scratch，什么都没有，镜像就是二进制本身的大小。我们最后选了alpine，因为偶尔还是需要进容器排查问题。

.dockerignore也很重要但经常被忽略。构建的时候Docker会把整个上下文目录发给daemon，如果里面有.git、node_modules、测试数据之类的，不仅构建慢，还容易被COPY进镜像。

![](/images/wx20260722.png)

还有一些细节。apt-get install的时候加--no-install-recommends可以少装很多推荐包，装完在同一个RUN里把/var/lib/apt/lists清掉。pip install加--no-cache-dir。多个RUN命令合并成一个可以减少层数。这些加起来我们又省了几十MB。

最后推荐一个工具dive，可以逐层查看镜像里的文件，很容易发现哪一层占了大空间，哪些文件是不应该存在的。

总的来说，镜像优化是一个持续的过程，需要在实践中不断摸索。希望本文对大家有所帮助。
