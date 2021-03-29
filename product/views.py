from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Product 
from .forms import UploadFileForm
from xlrd import XLRDError
import xlrd

# Create your views here.
"""
input:HttpRequest
Output: Redirect to an html with a context full of prices filtered

Filter the database and return the prices that match the name given.
"""
def price_view(request):
#	if request.method == 'GET':
#		search_query = request.GET.get('search_bar')
#		product_list = Product.objects.all().filter(name__icontains = search_query)
#		context = {
#		'product_list': product_list
#		}
		return render(request,'product/price_view.html',get_prices(request))


"""
input:HttpRequest
Output: 
Load prices from a file or given by the user
For loading from file, I use xlrd, being more simple for the user 
"""
def load_base_view(request):
# Load prices from a file 
	if request.method == "POST" and 'xls' in request.POST:
		form = UploadFileForm(request.POST,request.FILES)
		if form.is_valid():
			print("form valid")
			excel_file=request.FILES['file']
			try:
				prices_book = xlrd.open_workbook(file_contents = excel_file.read())
			except XLRDError:
				return render(request,'product/bad_file.html',{})
			prices = prices_book.sheet_by_index(0)
			print("archivo tiene {} columnas".format(prices.ncols))
			repeated_price_names	= save_products_from_file(prices)
			context= { 'name_list' : repeated_price_names }
		return render(request,'product/succesfull_file_load_view.html',context)


# Load prices manually, one by one.
	if(request.method == "POST"):
		created = save_single_product(request)
		if(created != False):
			return render(request,'product/repeated_price.html',{})
		if('save_and_exit' in request.POST):
			return render(request,'searchbar.html',{})
		else:
			return render(request,'product/succesfull_single_price_load.html',{})
	return render(request,'product/load_base.html',{})



def modify_product_view(request):
# Single_price
	if 'single' in request.GET:
		context = get_prices(request)
		return render(request,'product/select_price_to_base.html',context)

# Load prices from a file 
	if 'xls' in request.POST:
		form = UploadFileForm(request.POST,request.FILES)
		if form.is_valid():
			excel_file=request.FILES['file']
			try:
				prices_book = xlrd.open_workbook(file_contents = excel_file.read())
			except XLRDError:
				return render(request,'product/bad_file.html',{})
			prices = prices_book.sheet_by_index(0)
			not_found_product = modify_products_from_file(prices)
			context= { 'name_list' : not_found_product }
		return render(request,'product/successful_price_modification_from_file.html',context)
	return render(request,'product/modify_base_view.html',{})





def update_single_price_view(request):
	if request.method == 'GET' and 'single' in request.GET:
		context = get_prices(request)
		return render(request,'product/select_price_to_modify.html',context)

	if request.method == 'POST':
		list_to_process = request.POST.getlist('Modificar')
		count = 0
		request.session['product_id_list'] = list_to_process
		return redirect('update', position_id = count)
	return render(request,'product/select_price_to_modify.html',{})



def update_price_view(request,position_id):
	list_to_process = request.session['product_id_list']
	if request.method == 'POST':
		product = get_object_or_404(Product,pk=list_to_process[position_id-1])
		save_modifications(request,product)
	if (position_id < len(list_to_process)):
		product = get_object_or_404(Product,pk=list_to_process[position_id])
		context = {
			'product' : product,
			'count': position_id+1}
	else:
			return render(request,'product/successful_single_price_modify.html',{})	
	return render(request,'product/update_single_price_view.html',context)
		


#https://stackoverflow.com/questions/25163308/get-the-values-of-multiple-checkboxes-in-django
def delete_single_price_view(request):
	if request.method == 'POST':
		to_delete = request.POST.getlist('Eliminar')
		for product_id in to_delete:
			product = get_object_or_404(Product,pk=product_id)
			product.delete()
		return render(request,'product/successful_delete.html',{})	
	if request.method == 'GET':
		context = get_prices(request)
	return render(request,'product/select_price_to_delete.html',context)



def modify_price_from_file_view(resquest):
	if request.method == 'GET':
		context = get_prices(request)   
	if request.method == 'POST':
		to_modify = request.POST.getlist('Modificar')
		for product_id in to_modify:
			product = get_object_or_404(Product,pk=product_id)
			return render(request,'product/update_single_price_view',product)
	return render(request,'product/select_price_to_modify.html',context)	

#------------HANDLERS------------#
"""
input:HttpRequest
Output: Boolean

Check if the price is already in the database. If its not, then save it. But 
if its a repeated price, warn the user about it.
"""
def save_single_product(request):
	name = request.POST['name']
	price = request.POST['price']
	description = request.POST['description']
	product = Product.objects.all().filter(name__iexact = name)
	if product:
		created = True
	if not product:
		product = Product(name=name,price=price,description=description)
		product.save()
		created = False
	return(created)

#	new_product,created = Product.objects.get_or_create(name=name,price=price,description=description)
#	if(created != True):
#		return render(request,'product/repeated_price.html',{})
#	return(created)

"""
input:HttpRequest
Output: None

Check one by one every price of the list, if they are already in the database. If  they are not, then save it.
"""
def save_products_from_file(prices):
	description = ""
	repeated_products = []
	for i in range(0,prices.nrows):
		name = prices.cell_value(i,0)
		price = prices.cell_value(i,1)
		if(prices.ncols > 2):
			description = prices.cell_value(i,2)
		product = Product.objects.all().filter(name__iexact = name)
		if not product:
			product = Product(name=name,price=price,description=description)
			product.save()
		else:
			repeated_products.append(name)
	return(repeated_products)

		#new_product,created = Product.objects.get_or_create(name=name,price=price,description=description)


def modify_products_from_file(prices):
	description = ""
	not_found_product = []
	for i in range(0,prices.nrows):
		name = prices.cell_value(i,0)
		price = prices.cell_value(i,1)
		if(prices.ncols > 2):
			description = prices.cell_value(i,2)
		product = Product.objects.all().filter(name__iexact = name)
		if not product:
			not_found_product.append(name)
		else:
			product.update(price = price)
	return(not_found_product)



def get_prices(request):
	if request.method == 'GET':
		search_query = request.GET.get('search_bar')
		product_list = Product.objects.all().filter(name__icontains = search_query)
		context = {
		'product_list': product_list
		}
		return(context)

def save_modifications(request,product):
	if(request.method =='POST'):
		new_price = request.POST['new_price']
		product.price = new_price
		product.save()