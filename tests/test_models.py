from src.models import Banner, Customer

def test_banner_from_customer():
	c = Customer(name="A", age=20, cookie="cookie", banner_id=7)
	b = Banner.from_customer(c)
	assert b.visitor_cookie == "cookie"
	assert b.banner_id == 7
