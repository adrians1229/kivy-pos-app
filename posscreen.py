# main.py - Fixed version with proper quick stats functionality
import os
os.environ['KIVY_WINDOW']='sdl2'

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.lang import Builder
from kivy.metrics import dp, sp
from kivy.config import Config
from kivy.core.window import Window
from kivy.clock import Clock
from datetime import datetime, timedelta
import json
import os

# Force landscape orientation - Multiple methods to ensure it works
Config.set('graphics', 'orientation', 'landscape')
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')
Config.set('graphics', 'minimum_width', '800')
Config.set('graphics', 'minimum_height', '480')

# Additional window configuration
Window.size = (800, 480)
Window.minimum_width = 800
Window.minimum_height = 480

# Load the KV file
Builder.load_file("posscreen.kv")


class OrderItem:
    def __init__(self, name, price, quantity=1):
        self.name = name
        self.price = price
        self.quantity = quantity
        self.date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @property
    def total(self):
        return self.price * self.quantity


class TransactionRecord:
    def __init__(self, order_id, date_time, customer_name, items, total, payment, change):
        self.order_id = order_id
        self.date_time = date_time
        self.customer_name = customer_name
        self.items = items  # List of OrderItem objects
        self.total = total
        self.payment = payment
        self.change = change


class StartScreen(Screen):
    def on_start_pressed(self):
        """Handle start button press"""
        self.manager.current = 'dashboard'


class DashboardScreen(Screen):
    product_name = StringProperty("Ginger Calamansi")
    product_price = NumericProperty(25.0)
    customer_name = StringProperty("")
    payment_amount = NumericProperty(0.0)
    change_amount = NumericProperty(0.0)
    order_items = ListProperty([])
    current_quantity = NumericProperty(1)
    
    # Quick Stats Properties - Fixed with proper initialization
    today_sales = NumericProperty(0.0)
    today_transactions = NumericProperty(0)
    current_order_items = NumericProperty(0)
    current_order_total = NumericProperty(0.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.order_data = []
        self.transaction_history = []
        self.customer_counter = 1
        
        # Schedule initialization after the widget is fully created
        Clock.schedule_once(self.initialize_data, 0.1)

    def initialize_data(self, dt):
        """Initialize data after the widget is fully created"""
        self.load_transaction_history()
        self.update_quick_stats()

    def load_transaction_history(self):
        """Load transaction history from file"""
        try:
            if os.path.exists('transaction_history.json'):
                with open('transaction_history.json', 'r') as f:
                    data = json.load(f)
                    for record in data:
                        items = [OrderItem(item['name'], item['price'], item['quantity'])
                                 for item in record['items']]
                        transaction = TransactionRecord(
                            record['order_id'],
                            record['date_time'],
                            record['customer_name'],
                            items,
                            record['total'],
                            record['payment'],
                            record['change']
                        )
                        self.transaction_history.append(transaction)
                    # Update customer counter based on existing records
                    max_customer_num = 0
                    for transaction in self.transaction_history:
                        if transaction.customer_name.startswith('Customer '):
                            try:
                                num = int(transaction.customer_name.split(' ')[1])
                                max_customer_num = max(max_customer_num, num)
                            except:
                                pass
                    self.customer_counter = max_customer_num + 1
        except Exception as e:
            print(f"Error loading transaction history: {e}")

    def save_transaction_history(self):
        """Save transaction history to file"""
        try:
            data = []
            for transaction in self.transaction_history:
                items_data = [{'name': item.name, 'price': item.price, 'quantity': item.quantity}
                              for item in transaction.items]
                data.append({
                    'order_id': transaction.order_id,
                    'date_time': transaction.date_time,
                    'customer_name': transaction.customer_name,
                    'items': items_data,
                    'total': transaction.total,
                    'payment': transaction.payment,
                    'change': transaction.change
                })
            with open('transaction_history.json', 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving transaction history: {e}")

    def calculate_today_stats(self):
        """Calculate today's sales and transaction statistics"""
        today = datetime.now().date()
        today_sales = 0.0
        today_transactions = 0
        
        for transaction in self.transaction_history:
            try:
                trans_date = datetime.strptime(transaction.date_time, '%Y-%m-%d %H:%M:%S').date()
                if trans_date == today:
                    today_sales += transaction.total
                    today_transactions += 1
            except Exception as e:
                print(f"Error parsing date: {e}")
        
        self.today_sales = today_sales
        self.today_transactions = today_transactions

    def update_quick_stats(self):
        """Update all quick stats - Fixed version"""
        # Calculate today's stats
        self.calculate_today_stats()
        
        # Update current order stats
        self.current_order_items = len(self.order_data)
        self.current_order_total = sum(item.total for item in self.order_data)
        
        # Debug print to verify values are updating
        print(f"Quick Stats Updated:")
        print(f"  Today Sales: ₱{self.today_sales:.2f}")
        print(f"  Today Transactions: {self.today_transactions}")
        print(f"  Current Order Items: {self.current_order_items}")
        print(f"  Current Order Total: ₱{self.current_order_total:.2f}")

    def get_customer_name(self):
        """Get customer name or generate default name"""
        if self.customer_name.strip():
            return self.customer_name.strip()
        else:
            name = f"Customer {self.customer_counter}"
            self.customer_counter += 1
            return name

    def increase_quantity(self):
        """Increase quantity"""
        self.current_quantity += 1

    def decrease_quantity(self):
        """Decrease quantity"""
        if self.current_quantity > 1:
            self.current_quantity -= 1

    def on_payment_change(self, text):
        """Handle payment input changes safely"""
        try:
            self.payment_amount = float(text) if text else 0
            self.calculate_change()
        except ValueError:
            self.payment_amount = 0
            self.calculate_change()

    def add_to_order(self):
        """Add item to order with specified quantity"""
        # Check if item already exists
        for item in self.order_data:
            if item.name == self.product_name:
                item.quantity += self.current_quantity
                self.update_order()
                return

        # Add new item
        new_item = OrderItem(self.product_name, self.product_price, self.current_quantity)
        self.order_data.append(new_item)
        self.update_order()

        # Reset quantity to 1 after adding
        self.current_quantity = 1

    def update_order(self):
        """Update order display"""
        self.order_items = [(item.name, item.quantity, item.price, item.total, item.date_time) for item in
                            self.order_data]
        self.calculate_totals()
        self.update_order_table()
        
        # Force update of quick stats
        self.update_quick_stats()

    def update_order_table(self):
        """Update the order table display"""
        if hasattr(self, 'ids') and 'order_table' in self.ids:
            table = self.ids.order_table
            table.clear_widgets()

            # Add header
            header = GridLayout(cols=5, size_hint_y=None, height=dp(30))
            header.add_widget(Label(text="Qty", font_size=sp(10), bold=True, color=(0, 0, 0, 1)))
            header.add_widget(Label(text="Item", font_size=sp(10), bold=True, color=(0, 0, 0, 1)))
            header.add_widget(Label(text="Price", font_size=sp(10), bold=True, color=(0, 0, 0, 1)))
            header.add_widget(Label(text="Total", font_size=sp(10), bold=True, color=(0, 0, 0, 1)))
            header.add_widget(Label(text="Time", font_size=sp(10), bold=True, color=(0, 0, 0, 1)))
            table.add_widget(header)

            # Add items
            for item in self.order_data:
                row = GridLayout(cols=5, size_hint_y=None, height=dp(25))
                row.add_widget(Label(text=str(item.quantity), font_size=sp(9), color=(0, 0, 0, 1)))
                row.add_widget(Label(text=item.name[:15], font_size=sp(9), color=(0, 0, 0, 1)))
                row.add_widget(Label(text=f"₱{item.price:.2f}", font_size=sp(9), color=(0, 0, 0, 1)))
                row.add_widget(Label(text=f"₱{item.total:.2f}", font_size=sp(9), color=(0, 0, 0, 1)))
                row.add_widget(Label(text=item.date_time[11:16], font_size=sp(9), color=(0, 0, 0, 1)))
                table.add_widget(row)

    def calculate_totals(self):
        """Calculate total amount"""
        total = sum(item.total for item in self.order_data)
        if hasattr(self, 'ids') and 'total_label' in self.ids:
            self.ids.total_label.text = f"TOTAL: ₱{total:.2f}"
        self.calculate_change()

    def calculate_change(self):
        """Calculate change amount"""
        total = sum(item.total for item in self.order_data)
        self.change_amount = self.payment_amount - total
        if hasattr(self, 'ids') and 'change_label' in self.ids:
            self.ids.change_label.text = f"Change: ₱{self.change_amount:.2f}"

    def view_order(self):
        """Display current order in a popup"""
        if not self.order_data:
            # Show empty order message
            popup = Popup(
                title='Order Details',
                content=Label(
                    text='No items in order yet.',
                    text_size=(None, None),
                    halign='center',
                    valign='middle',
                    font_size=sp(20),
                    color=(0, 0, 0, 1)
                ),
                size_hint=(0.85, 0.7),
                auto_dismiss=True
            )
            popup.open()
            return

        # Create order details content
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))

        # Add scrollable order list
        scroll = ScrollView()
        order_layout = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        order_layout.bind(minimum_height=order_layout.setter('height'))

        # Add header
        header = Label(
            text='CURRENT ORDER',
            bold=True,
            font_size=sp(24),
            size_hint_y=None,
            height=dp(60),
            color=(0.2, 0.6, 0.2, 1)
        )
        order_layout.add_widget(header)

        # Add order items
        for item in self.order_data:
            item_text = f"{item.name} x{item.quantity} = ₱{item.total:.2f} | {item.date_time}"
            item_label = Label(
                text=item_text,
                font_size=sp(18),
                size_hint_y=None,
                height=dp(50),
                text_size=(None, None),
                halign='left',
                color=(0, 0, 0, 1)
            )
            order_layout.add_widget(item_label)

        # Add total
        total = sum(item.total for item in self.order_data)
        total_label = Label(
            text=f"TOTAL: ₱{total:.2f}",
            bold=True,
            font_size=sp(22),
            size_hint_y=None,
            height=dp(60),
            color=(0.2, 0.6, 0.2, 1)
        )
        order_layout.add_widget(total_label)

        scroll.add_widget(order_layout)
        content.add_widget(scroll)

        # Create and show popup
        popup = Popup(
            title='Order Details',
            content=content,
            size_hint=(0.9, 0.8),
            auto_dismiss=True
        )
        popup.open()

    def filter_transactions_by_period(self, period):
        """Filter transactions by time period"""
        now = datetime.now()

        if period == 'daily':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'weekly':
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'monthly':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            return self.transaction_history

        filtered = []
        for transaction in self.transaction_history:
            try:
                trans_date = datetime.strptime(transaction.date_time, '%Y-%m-%d %H:%M:%S')
                if trans_date >= start_date:
                    filtered.append(transaction)
            except Exception as e:
                print(f"Error filtering transaction: {e}")

        return filtered

    def view_transaction_history(self):
        """Display transaction history selection popup"""
        # Create content for period selection
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))

        # Add title
        title = Label(
            text='Select Time Period',
            font_size=sp(20),
            bold=True,
            size_hint_y=None,
            height=dp(40),
            color=(0.2, 0.6, 0.2, 1)
        )
        content.add_widget(title)

        # Add buttons for different periods with responsive sizing
        button_layout = BoxLayout(orientation='vertical', spacing=dp(5))

        daily_btn = Button(
            text='Daily Sales',
            font_size=sp(16),
            size_hint_y=None,
            height=dp(45),
            background_color=(0.2, 0.6, 0.2, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        daily_btn.bind(on_press=lambda x: self.show_filtered_history('daily'))

        weekly_btn = Button(
            text='Weekly Sales',
            font_size=sp(16),
            size_hint_y=None,
            height=dp(45),
            background_color=(0.1, 0.4, 0.8, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        weekly_btn.bind(on_press=lambda x: self.show_filtered_history('weekly'))

        monthly_btn = Button(
            text='Monthly Sales',
            font_size=sp(16),
            size_hint_y=None,
            height=dp(45),
            background_color=(0.6, 0.4, 0.8, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        monthly_btn.bind(on_press=lambda x: self.show_filtered_history('monthly'))

        all_btn = Button(
            text='All Transactions',
            font_size=sp(16),
            size_hint_y=None,
            height=dp(45),
            background_color=(0.8, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        all_btn.bind(on_press=lambda x: self.show_filtered_history('all'))

        button_layout.add_widget(daily_btn)
        button_layout.add_widget(weekly_btn)
        button_layout.add_widget(monthly_btn)
        button_layout.add_widget(all_btn)

        content.add_widget(button_layout)

        # Create and show popup with responsive sizing
        self.period_popup = Popup(
            title='Transaction History',
            content=content,
            size_hint=(0.8, 0.6),
            auto_dismiss=True
        )
        self.period_popup.open()

    def show_filtered_history(self, period):
        """Display filtered transaction history"""
        # Close the period selection popup
        if hasattr(self, 'period_popup'):
            self.period_popup.dismiss()

        # Get filtered transactions
        if period == 'all':
            filtered_transactions = self.transaction_history
            title_text = 'ALL TRANSACTIONS'
        else:
            filtered_transactions = self.filter_transactions_by_period(period)
            title_text = f'{period.upper()} TRANSACTIONS'

        if not filtered_transactions:
            popup = Popup(
                title='Transaction History',
                content=Label(
                    text=f'No {period} transactions yet.',
                    text_size=(None, None),
                    halign='center',
                    valign='middle',
                    font_size=sp(20),
                    color=(0, 0, 0, 1)
                ),
                size_hint=(0.9, 0.8),
                auto_dismiss=True
            )
            popup.open()
            return

        # Create scrollable content
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
        scroll = ScrollView()

        # Create table-like layout
        table_layout = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        table_layout.bind(minimum_height=table_layout.setter('height'))

        # Add header
        header = Label(
            text=title_text,
            bold=True,
            font_size=sp(24),
            size_hint_y=None,
            height=dp(60),
            color=(0.2, 0.6, 0.2, 1)
        )
        table_layout.add_widget(header)

        # Calculate total sales for the period
        total_sales = sum(transaction.total for transaction in filtered_transactions)
        sales_summary = Label(
            text=f'Total Sales: ₱{total_sales:.2f} | Transactions: {len(filtered_transactions)}',
            bold=True,
            font_size=sp(18),
            size_hint_y=None,
            height=dp(50),
            color=(0.1, 0.4, 0.8, 1)
        )
        table_layout.add_widget(sales_summary)

        # Add transactions (most recent first)
        for transaction in reversed(filtered_transactions):
            # Create transaction container
            trans_container = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None)
            trans_container.bind(minimum_height=trans_container.setter('height'))

            # Transaction header
            trans_header = Label(
                text=f"Order: {transaction.order_id} | Date: {transaction.date_time} | Customer: {transaction.customer_name}",
                font_size=sp(16),
                bold=True,
                color=(0, 0, 0, 1),
                size_hint_y=None,
                height=dp(40),
                text_size=(None, None),
                halign='left'
            )
            trans_container.add_widget(trans_header)

            # Items
            for item in transaction.items:
                item_label = Label(
                    text=f"  {item.name} x{item.quantity} = ₱{item.total:.2f}",
                    font_size=sp(15),
                    color=(0.3, 0.3, 0.3, 1),
                    size_hint_y=None,
                    height=dp(35),
                    text_size=(None, None),
                    halign='left'
                )
                trans_container.add_widget(item_label)

            # Transaction total
            total_label = Label(
                text=f"Total: ₱{transaction.total:.2f} | Paid: ₱{transaction.payment:.2f} | Change: ₱{transaction.change:.2f}",
                font_size=sp(16),
                bold=True,
                color=(0.2, 0.6, 0.2, 1),
                size_hint_y=None,
                height=dp(40),
                text_size=(None, None),
                halign='left'
            )
            trans_container.add_widget(total_label)

            # Add separator
            separator = Label(
                text="─" * 50,
                font_size=sp(14),
                size_hint_y=None,
                height=dp(30),
                color=(0.7, 0.7, 0.7, 1)
            )
            trans_container.add_widget(separator)

            table_layout.add_widget(trans_container)

        scroll.add_widget(table_layout)
        content.add_widget(scroll)

        # Create and show popup
        popup = Popup(
            title=f'{period.title()} Transaction History',
            content=content,
            size_hint=(0.95, 0.9),
            auto_dismiss=True
        )
        popup.open()

    def clear_order(self):
        """Clear the current order"""
        self.order_data.clear()
        self.update_order()
        if hasattr(self, 'ids'):
            if 'payment_input' in self.ids:
                self.ids.payment_input.text = ''
            if 'customer_name_input' in self.ids:
                self.ids.customer_name_input.text = ''
        self.customer_name = ""
        self.payment_amount = 0.0
        self.change_amount = 0.0
        self.current_quantity = 1
        # Force update of quick stats after clearing
        self.update_quick_stats()

    def process_payment(self):
        """Process the payment and complete the transaction"""
        if not self.order_data:
            popup = Popup(
                title='Error',
                content=Label(
                    text='No items in order.',
                    text_size=(None, None),
                    halign='center',
                    valign='middle',
                    font_size=sp(20),
                    color=(0, 0, 0, 1)
                ),
                size_hint=(0.7, 0.4),
                auto_dismiss=True
            )
            popup.open()
            return

        total = sum(item.total for item in self.order_data)

        if self.payment_amount < total:
            popup = Popup(
                title='Error',
                content=Label(
                    text='Insufficient payment amount.',
                    text_size=(None, None),
                    halign='center',
                    valign='middle',
                    font_size=sp(20),
                    color=(0, 0, 0, 1)
                ),
                size_hint=(0.7, 0.4),
                auto_dismiss=True
            )
            popup.open()
            return

        # Create transaction record
        order_id = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        customer_name = self.get_customer_name()

        # Create a copy of the order items
        items_copy = [OrderItem(item.name, item.price, item.quantity) for item in self.order_data]

        transaction = TransactionRecord(
            order_id=order_id,
            date_time=date_time,
            customer_name=customer_name,
            items=items_copy,
            total=total,
            payment=self.payment_amount,
            change=self.change_amount
        )

        # Add to transaction history
        self.transaction_history.append(transaction)

        # Save to file
        self.save_transaction_history()

        # Show success message
        success_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        success_label = Label(
            text='Transaction Completed Successfully!',
            bold=True,
            font_size=sp(22),
            color=(0.2, 0.6, 0.2, 1),
            size_hint_y=None,
            height=dp(60)
        )
        success_content.add_widget(success_label)

        details_label = Label(
            text=f'Order ID: {order_id}\nCustomer: {customer_name}\nTotal: ₱{total:.2f}\nPayment: ₱{self.payment_amount:.2f}\nChange: ₱{self.change_amount:.2f}',
            font_size=sp(16),
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=dp(150)
        )
        success_content.add_widget(details_label)

        popup = Popup(
            title='Transaction Complete',
            content=success_content,
            size_hint=(0.8, 0.6),
            auto_dismiss=True
        )
        popup.open()

        # Clear the order and update quick stats
        self.clear_order()
        # Force update of quick stats after successful transaction
        self.update_quick_stats()

    def remove_item(self, item_name):
        """Remove an item from the order"""
        self.order_data = [item for item in self.order_data if item.name != item_name]
        self.update_order()


class POSApp(App):
    def build(self):
        # Additional window settings to ensure landscape mode
        Window.bind(on_resize=self.maintain_landscape)

        sm = ScreenManager()
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        return sm

    def maintain_landscape(self, window, width, height):
        """Maintain landscape orientation"""
        if width < height:
            # If window becomes portrait, swap dimensions
            Window.size = (height, width)

    def on_start(self):
        """Called when the app starts"""
        # Force landscape on app start
        Window.size = (800, 480)


if __name__ == '__main__':
    POSApp().run()
