import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='dockertarpusher',  
     version='0.16',
     author="Adam Raźniewski",
     author_email="adam@razniewski.eu",
     description="Docker tar pusher to registry without docker daemon",
     long_description=long_description,
     keywords="docker tar dockertar registry",
     entry_points = {
        'console_scripts': ['docker-tar-push=dockertarpusher.command_line:main'],
    },
     long_description_content_type="text/markdown",
     url="https://github.com/Razikus/dockerregistrypusher",
     packages=["dockertarpusher"],
     install_requires=[
         "requests"
     ],
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],

 )