from datetime import date, timedelta
from io import BytesIO
from PIL import Image
from django.test import TestCase, Client
from django.core.files.base import File
from main.core.constants import Roles, PurchaseAndDeliveryTypes
from main.models import (
    User,
    Order,
    OrderItem,
    Product,
    SettingOptionHandler,
    SettingOption,
    SettingOptionImages,
)


class BaseConfiguration(TestCase):

    ZAKAZSCHIK1_LOGIN = 'zakazschik1@testshop.ru'
    ZAKAZSCHIK2_LOGIN = 'zakazschik2@testshop.ru'
    ZAKUPSCHIK_LOGIN = 'zakupschik@testshop.ru'
    ADMINISTRATOR_LOGIN = 'administrator@testshop.ru'
    PASSWORD = 'FakePass'

    def setUp(self) -> None:
        birth_date = date(1960, 10, 23)

        self.zakazschik1 = User(
            email=self.ZAKAZSCHIK1_LOGIN,
            phone='+7-999-23-12',
            delivery_address='Test Address 111',
            birth_date=birth_date,
            role=Roles.ZAKAZSCHIK,
        )
        self.zakazschik1.set_password(self.PASSWORD)
        self.zakazschik1.save()

        self.zakazschik2 = User(
            email=self.ZAKAZSCHIK2_LOGIN,
            phone='+7-999-23-55',
            delivery_address='Test Address 222',
            birth_date=birth_date - timedelta(weeks=100),
            role=Roles.ZAKAZSCHIK,
        )
        self.zakazschik2.set_password(self.PASSWORD)
        self.zakazschik2.save()

        self.zakupschik = User(
            email=self.ZAKUPSCHIK_LOGIN,
            phone='+7-555-11-22',
            delivery_address='Test Address 333',
            birth_date=birth_date + timedelta(weeks=55),
            role=Roles.ZAKUPSCHIK,
        )
        self.zakupschik.set_password(self.PASSWORD)
        self.zakupschik.save()

        self.administrator = User(
            email=self.ADMINISTRATOR_LOGIN,
            phone='+7-333-44-55',
            delivery_address='Test Address 444',
            birth_date=birth_date - timedelta(weeks=200),
            role=Roles.ADMINISTRATOR,
        )
        self.administrator.set_password(self.PASSWORD)
        self.administrator.save()

        SettingOptionHandler('extra_charge').value = 10     # 10%
        self.extra_charge = SettingOptionHandler('extra_charge').value

        self.client = Client()

    def tearDown(self) -> None:
        Order.objects.all().delete()
        OrderItem.objects.all().delete()
        Product.objects.all().delete()
        SettingOption.objects.all().delete()
        SettingOptionImages.objects.all().delete()

    @staticmethod
    def get_image_file(name='test.png', ext='png', size=(50, 50), color=(256, 0, 0)):
        file_obj = BytesIO()
        image = Image.new("RGBA", size=size, color=color)
        image.save(file_obj, ext)
        file_obj.seek(0)
        return File(file_obj, name=name)

    def check_for_created_objects(self, orders=0, order_items=0, products=0):
        self.assertEqual(Order.objects.count(), orders)
        self.assertEqual(OrderItem.objects.count(), order_items)
        self.assertEqual(Product.objects.count(), products)


class AuthenticationTestCase(BaseConfiguration):

    def test_login(self):
        is_logged_in = self.client.login(email=self.ZAKAZSCHIK1_LOGIN, password=self.PASSWORD)
        self.assertTrue(is_logged_in)


class OrderTestCase(BaseConfiguration):

    def setUp(self) -> None:
        super().setUp()
        self.client.login(email=self.ZAKAZSCHIK1_LOGIN, password=self.PASSWORD)

    def test_create_order(self):
        url = '/new_order/'
        data = {
            'images': [self.get_image_file(name) for name in ('prod1.png', 'prod2.png', 'prod3.png')]
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.check_for_created_objects(orders=1, order_items=3, products=3)

    def test_add_individual_products_to_order(self):
        order = Order.objects.create(created_by=self.zakazschik1, updated_by=self.zakazschik1)
        self.check_for_created_objects(orders=1, order_items=0, products=0)
        self.assertEqual(0, order.price)
        self.assertEqual(0, self.zakazschik1.balance)

        url = '/orders/{pk}/new_item/'.format(pk=order.pk)
        prod_price1 = 100
        prod_quantity1 = 5
        data = {
            'image': self.get_image_file(),
            'name': 'Boots',
            'price': prod_price1,
            'quantity': prod_quantity1,
            'place': '123-123',
            'delivery': PurchaseAndDeliveryTypes.PURCHASE_AND_DELIVERY,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.check_for_created_objects(orders=1, order_items=1, products=1)
        order.refresh_from_db()
        extra_charge1 = prod_price1 * prod_quantity1 * self.extra_charge / 100
        total_order_price1 = prod_price1 * prod_quantity1 + extra_charge1
        self.assertEqual(order.price, total_order_price1)
        total_user_balance1 = -(prod_price1 * prod_quantity1 + extra_charge1)
        self.zakazschik1.refresh_from_db()
        self.assertEqual(self.zakazschik1.balance, total_user_balance1)

        prod_price2 = 60
        prod_quantity2 = 7
        data = {
            'image': self.get_image_file(),
            'name': 'Boots2',
            'price': prod_price2,
            'quantity': prod_quantity2,
            'place': '222-222',
            'delivery': PurchaseAndDeliveryTypes.DELIVERY_ONLY,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.check_for_created_objects(orders=1, order_items=2, products=2)
        order.refresh_from_db()
        extra_charge2 = prod_price2 * prod_quantity2 * self.extra_charge / 100
        total_order_price2 = total_order_price1 + extra_charge2     # extra_charge only due to DELIVERY_ONLY
        self.assertEqual(order.price, total_order_price2)
        total_user_balance2 = total_user_balance1 - extra_charge2
        self.zakazschik1.refresh_from_db()
        self.assertEqual(self.zakazschik1.balance, total_user_balance2)

    def test_delete_individual_products(self):
        pass
