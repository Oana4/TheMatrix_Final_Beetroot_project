# TheMatrix

This web application was created using Django 4.1.5 as final project for Beetroot Academy's "Python Development" Course. It represents a taxi app which allows users to place orders, track their status, chat with both current order's driver and administrators of the company and also rate the drivers that they've interacted with. The data for our orders is retrieved from Google Maps using Google APIs.


## Authors

 - [Eduard Stan](https://github.com/EdyStan) {edigeorges50@gmail.com}
 - [Oana Sîrbu](https://github.com/Oana4) {sirbu.oana4@gmail.com}
 - [Anastasiya Sviderska](https://github.com/anastasiyasviderska) {aj@gumgumlab.com}


## Requirements

To continue with the development of this code, one should be up-to-date to all libraries that have been used. They can be easily installed using 

```bash
  pip install -r requirements.txt
```
To actually run the project, just write in the terminal the following command 

```bash
  python3 manage.py runserver
```
You may also need to create a new secret key for this Django project. Here you can find some nice instructions:
https://www.educative.io/answers/how-to-generate-a-django-secretkey
    
## Description

The main page of our app displays information about who we are, special offers, reviews from our customers/employees regarding the services and also some nice suprises.

When new users register in the application, they can choose their role (will they be drivers or passengers?) and they will be redirected to the coresponding register page. After registeration, the page will redirect the user to the login part. 

Right after logging in, one will be redirected to the special menu designed with a touch of autenticity for driver/passenger, depending the role that was chosen. 

The friendly interface for passenger menu functionality hides many backend lines of code, that in principle facilitate the following features: place an order/see status of current order, chat with current driver (if exists), open HelpDesk, rate a driver, change your password, see your balance and even add more money to your account. 

On the other side, when accesing his menu, a driver is capable of: seeing available orders, assigning an order and also starting the movement (set the order status to "in progress"). Moreover, he can also see his income (that increases with each finished order), chat with his passengers and with administrators. The possibility of changing the account's password exists here, too.

Have we managed to get your attention? If so, test our app and feel free to give us some advice and suggestions :)
