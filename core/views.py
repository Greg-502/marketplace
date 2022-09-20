from itertools import product
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import View, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView, UpdateView
from marketplace.models import Product, PurchasedProduct
from marketplace.forms import ProductForm
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.conf import settings
from django.http.response import HttpResponse, JsonResponse
from stripe.error import SignatureVerificationError
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from accounts.models import UserLibrary
import stripe

User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY

class HomeView(ListView):
    model = Product
    template_name = 'pages/index.html'
    form_class = ProductForm
    paginate_by = 18

    def get_queryset(self):
        return Product.objects.filter(active=True).order_by('-pk')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class
        context['title'] = 'Catalog'
        return context
    
class CreateProducts(LoginRequiredMixin, CreateView):
    model = Product
    template_name = "pages/forms/createProduct.html"
    form_class = ProductForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save(commit=False)
            form.instance.user = self.request.user
            form.save()
            messages.success(request, f'Product created successfully.')
            return redirect('/create/')
        messages.error(request, f'Form has some issue(s).')
        return super().post(request, *args, **kwargs)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create entries'
        return context

class ListProducts(LoginRequiredMixin, ListView):
    template_name = 'pages/listProducts.html'
    model = Product

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user).order_by('-pk')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Products list'
        return context
    
class UserLibraryList(LoginRequiredMixin, ListView):
    model = UserLibrary
    template_name = 'pages/myLibrary.html'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return UserLibrary.objects.get(user=user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My Purchases'
        return context

class EditProduct(LoginRequiredMixin, UpdateView):
    template_name = 'pages/forms/editForm.html'
    model = Product
    form_class = ProductForm
    success_message = "Product edited successfully."
    success_url = '/list/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit product'
        return context

class ProductDetail(DetailView):
    model = Product
    template_name = 'pages/detail.html'

    def get_context_data(self, **kwargs):
        has_access = False
        if self.request.user.is_authenticated:
            product = Product.objects.get(slug=self.kwargs['slug'])
            if product in self.request.user.library.products.all():
                has_access = True

        context = super().get_context_data(**kwargs)
        context['title'] = self.kwargs['slug']
        context['has_access'] = has_access
        context['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY
        return context
    
class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        product = Product.objects.get(slug=self.kwargs['slug'])
        customer=None
        customer_email=None

        if request.user.is_authenticated:
            if request.user.stripe_customer_id:
                customer=request.user.stripe_customer_id
            else:
                customer_email=request.user.email

        session = stripe.checkout.Session.create(
            customer=customer,
            customer_email=customer_email,

            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product.name,
                    },
                    'unit_amount': product.price,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/success/'),
            cancel_url=request.build_absolute_uri('/'),
            metadata={
                'product_id':product.id
            }
        )

        return JsonResponse({
            'id': session.id
        })

class SuccessView(TemplateView):
    template_name = "pages/success.html"

@csrf_exempt
def stripe_webhook(request, *args, **kwargs):
    CHECKOUT_SESSION_COMPLETED = "checkout.session.completed"

    payload = request.body
    signature_header = request.META["HTTP_STRIPE_SIGNATURE"]

    try:
        event = stripe.Webhook.construct_event(
            payload,
            signature_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        print(e)
        return HttpResponse(statu=400)
    except SignatureVerificationError as e:
        print(e)
        return HttpResponse(statu=400)

    # escuchar por pago exitoso
    if event["type"] == CHECKOUT_SESSION_COMPLETED:
        print(event)

        # quien pago por que cosa?
        product_id=event["data"]["object"]["metadata"]["product_id"]
        product = Product.objects.get(id=product_id)

        stripe_customer_id=event["data"]["object"]["customer"]

        # dar acceso al producto
        try:
            #revisar si el usuario ya tiene un customer ID
            user = User.objects.get(stripe_customer_id=stripe_customer_id)

            user.library.products.add(product)
            user.library.save()
        except User.DoesNotExist:
            #si el usuario no tiene customer ID, pero este si esta registrado en el sitio web
            stripe_customer_email = event["data"]["object"]["customer_details"]["email"]

            try:
                user = User.objects.get(email=stripe_customer_email)
                user.stripe_customer_id = stripe_customer_id
                user.library.products.add(product)
                user.library.save()
            except User.DoesNotExist:
                PurchasedProduct.objects.create(
                    email=stripe_customer_email,
                    product=product
                )

                send_mail(
                    subject="Create an account to access your content",
                    message="Please signup to access your products",
                    recipient_list=[stripe_customer_email],
                    from_email=settings.EMAIL_HOST_USER
                )

                pass
                
    return HttpResponse()

# class TestView(View):
#     def get(self, request, *args, **kwargs):
#         context = {}
#         return render(request, 'pages/test.html', context)
