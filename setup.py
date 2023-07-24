# _author: Coke
# _date: 2022/8/2 15:30

from setuptools import find_packages, setup

setup(
    name='subscribe-subway-capital',
    description='北京地铁进站预约程序',
    url='https://github.com/wangtao2213405054/subscribe-subway',
    version='1.2.1',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'requests',
        'click',
        'customtkinter',
        'chinesecalendar',
        'urllib3'
    ]
)
