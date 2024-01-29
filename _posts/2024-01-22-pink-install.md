---
layout: post
title: "Getting started with pink"
date: 2024-01-22
description: Efficiently pink install tutorial for linux newbies
tags: classes
categories: classes

toc:
  sidebar: left
---

# Installing and Setting up PINK Library on Linux

Welcome to the world of image processing with the PINK library! PINK is an open-source library designed for image analysis and processing tasks. In this brief tutorial, I'll guide you through the process of downloading, installing, and setting up PINK on your Linux machine. We will also delve into some basic Linux commands to facilitate the installation process.

The installation involves downloading the PINK library, performing the compilation in the local `/tmp` directory to optimize the process, and finally, setting up the necessary environment variables for seamless usage. By the end of this tutorial, you'll have PINK installed and configured, ready to explore its capabilities.

## 1. Download PINK Library in /tmp

In situations where the compilation of PINK might be time-consuming due to communication delays, it's beneficial to perform the compilation in the local `/tmp` directory and then move the compiled files to the user's working space.
Navigate to the `/tmp` directory, where you will perform the compilation:

- Enter into the `/tmp` directory.
- Download PINK library at the following address: [https://perso.esiee.fr/~coupriem/pink.tgz](https://perso.esiee.fr/~coupriem/pink.tgz). It can be easily performed with the `wget` command.

```bash
cd /tmp
wget https://perso.esiee.fr/~coupriem/pink.tgz
```

## 2. Uncompress PINK

- Use the `tar` command to extract the contents of the `pink.tgz` file:

```bash
tar -xvzf /tmp/pink.tgz
```

## 3. Compile PINK

- Enter the extracted directory with `cd` and compile PINK using the provided `makelin` script.

```bash
./makelin
```

> Don't worry if there's an error at the end of compilation. Doxygen is a documentation tool. PINK documentation can be found online: [PINK documentation](https://perso.esiee.fr/~coupriem/Pink/doc/html/).

## 4. Move PINKtmp to your Working Space

- After the compilation is complete, move the compiled `PINKtmp` directory to your user's working space. Replace `[user_working_space]` with the path to the user's working directory:

```bash
mv /tmp/PINKtmp user_working_space
```

## 5. Create & edit .pink.start file

When a user types a command in the terminal, the system needs to locate the corresponding executable file to run that command. Instead of providing the full path to the executable every time, the **PATH** variable allows users to specify a set of directories where the system should search for executables.

**An example.** If the **PATH** variable is set as follows:

```bash
export PATH=/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin
```

And the user types `ls` in the terminal:

1. The system looks for `ls` in `/usr/local/bin`. If found, it executes that version of ls.
2. If not found, it looks in `/bin`.
3. If still not found, it looks in `/usr/bin`.
4. If the executable is found in any of these directories, the system executes the command. Otherwise, it displays an "command not found" error.

You can display your PATH as follows:

```bash
echo $PATH
```

Our goal is to add the path to the PINK executable to the PATH so that you can run any PINK command from anywhere.

- Create and open the `.pink.start` file with a text editor (e.g., `nano` if you are blind, `vim` if you are brave, or `gedit` if you like user interfaces)

```bash
touch ~/.pink.start
gedit ~/.pink.start &
```

- Add the following two lines to the file, replacing `[user_working_space]` with the actual path to the user's working space:

```bash
export PINK=user_working_space/Pinktmp
export PATH=$PATH:$PINK/linux/bin:$PINK/scripts:$PINK/tcl
```

> #### WARNING
>
> A file beginning with a dot (`.`) is considered a hidden file. As a result it may not show up in your explorer.
> To view hidden files in a Unix-like terminal, you can use the `-a` option with the `ls` command:
> `ls -a`
{: .block-warning }


## 6. Source .pink.start

Before using PINK in a new terminal session, run the following command to source the `.pink.start` file:

```bash
source ~/.pink.start
```

Now, PINK is installed and configured on your Linux system. You can print your **PATH** variable to visualize the change. If you really want to be sure type `dilation`.