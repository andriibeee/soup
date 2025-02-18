import pytest
from bs4 import BeautifulSoup

from exceptions import (
    FuckedUpMarkupError,
    InvalidPagerTextError,
    InvalidAvailabilityClassError,
    MissingTitleError,
    MissingPriceError,
)
from scraper import gauge_availability, parse_book, parse_pages_count


def test_parse_pages_count_valid():
    assert parse_pages_count("Page 3 of 10") == 10


def test_parse_pages_count_single_page():
    assert parse_pages_count("Page 1 of 1") == 1


def test_parse_pages_count_extra_whitespace():
    assert parse_pages_count("Page  5  of  20 ") == 20


def test_parse_pages_count_newlines():
    assert parse_pages_count("Page  5 \n of 20") == 20


def test_parse_pages_count_empty_string():
    with pytest.raises(InvalidPagerTextError, match="Empty string provided"):
        parse_pages_count("")


def test_parse_pages_count_string_of_whitespaces():
    with pytest.raises(InvalidPagerTextError, match="Empty string provided"):
        parse_pages_count("  ")


def test_parse_pages_count_missing_page():
    with pytest.raises(
        InvalidPagerTextError, match="Could not extract pages count from string: 3 of 4"
    ):
        parse_pages_count("3 of 4")


def test_parse_pages_count_non_numeric():
    with pytest.raises(
        InvalidPagerTextError,
        match="Could not extract pages count from string: Page 3 of x",
    ):
        parse_pages_count("Page 3 of x")


#


def test_gauge_availability_instock():
    html = '<div><p class="availability instock">In stock</p></div>'
    soup = BeautifulSoup(html, "html.parser")
    assert gauge_availability(soup) is True


def test_gauge_availability_unexpected_state():
    html = '<div><p class="availability unknown">In stock</p></div>'
    soup = BeautifulSoup(html, "html.parser")
    with pytest.raises(
        InvalidAvailabilityClassError,
        match="Unexpected availability class in element: \\['availability', 'unknown'\\]. Expected 'instock' or 'outofstock'",
    ):
        gauge_availability(soup)


def test_gauge_availability_outofstock():
    html = '<div><p class="availability outofstock">Out of stock</p></div>'
    soup = BeautifulSoup(html, "html.parser")
    assert gauge_availability(soup) is False


def test_gauge_availability_missing_state():
    html = '<div><p class="availability">Unknown</p></div>'
    soup = BeautifulSoup(html, "html.parser")
    with pytest.raises(
        InvalidAvailabilityClassError,
        match="Unexpected availability class in element: \\['availability'\\]. Expected 'instock' or 'outofstock'",
    ):
        gauge_availability(soup)


def test_gauge_availability_no_availability_class():
    html = '<div><p class="instock">In stock</p></div>'
    soup = BeautifulSoup(html, "html.parser")
    with pytest.raises(FuckedUpMarkupError):
        gauge_availability(soup)


def test_gauge_availability_no_classes():
    html = "<div><p>In stock</p></div>"
    soup = BeautifulSoup(html, "html.parser")
    with pytest.raises(FuckedUpMarkupError):
        gauge_availability(soup)


def test_gauge_availability_empty_container():
    html = "<div></div>"
    soup = BeautifulSoup(html, "html.parser")
    with pytest.raises(FuckedUpMarkupError):
        gauge_availability(soup)


#


def test_parse_book():
    html = """
    <article class="product_pod">
            <div class="image_container">
                    <a href="the-invention-of-wings_448/index.html"><img src="../media/cache/62/fa/62fa1e72f06f05762db5d9cedf654153.jpg" alt="The Invention of Wings" class="thumbnail"></a>
            </div>
                <p class="star-rating One">
                    <i class="icon-star"></i>
                    <i class="icon-star"></i>
                    <i class="icon-star"></i>
                    <i class="icon-star"></i>
                    <i class="icon-star"></i>
                </p>
 <h3><a href="the-invention-of-wings_448/index.html" title="The Invention of Wings">The Invention of Wings</a></h3>
<div class="product_price">
<p class="price_color">£37.34</p>
<p class="instock availability">
    <i class="icon-ok"></i>
        In stock
</p>
    <form>
        <button type="submit" class="btn btn-primary btn-block" data-loading-text="Adding...">Add to basket</button>
    </form>
            </div>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    book = parse_book(soup.find("article", class_="product_pod"))
    assert book.title == "The Invention of Wings"
    assert book.price == "£37.34"
    assert book.available is True


def test_parse_book_long_title():
    html = """
<article class="product_pod">
            <div class="image_container">
                    <a href="catalogue/a-light-in-the-attic_1000/index.html"><img src="media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg" alt="A Light in the Attic" class="thumbnail"></a>
            </div>
                <p class="star-rating Three">
                    <i class="icon-star"></i>
                    <i class="icon-star"></i>
                    <i class="icon-star"></i>
                    <i class="icon-star"></i>
                    <i class="icon-star"></i>
                </p>
            <h3><a href="catalogue/a-light-in-the-attic_1000/index.html" title="A Light in the Attic">A Light in the ...</a></h3>
            <div class="product_price">
        <p class="price_color">£51.77</p>
<p class="instock availability">
    <i class="icon-ok"></i>
        In stock
</p>
    <form>
        <button type="submit" class="btn btn-primary btn-block" data-loading-text="Adding...">Add to basket</button>
    </form>
            </div>
    </article>
        """
    soup = BeautifulSoup(html, "html.parser")
    book = parse_book(soup.find("article", class_="product_pod"))
    assert book.title == "A Light in the Attic"
    assert book.price == "£51.77"
    assert book.available is True


def test_parse_book_bratty_price_element():
    html = """
    <article class="product_pod">
            <div class="image_container">
                    <a href="the-invention-of-wings_448/index.html"><img src="../media/cache/62/fa/62fa1e72f06f05762db5d9cedf654153.jpg" alt="The Invention of Wings" class="thumbnail"></a>
            </div>
                <p class="star-rating One">
                    <i class="icon-star"></i>
                    <i class="icon-star"></i>
                    <i class="icon-star"></i>
                    <i class="icon-star"></i>
                    <i class="icon-star"></i>
                </p>
 <h3><a href="the-invention-of-wings_448/index.html" title="The Invention of Wings">The Invention of Wings</a></h3>
<div class="product_price">
<p class="price_color">£37.<br/>34</p>
<p class="instock availability">
    <i class="icon-ok"></i>
        In stock
</p>
    <form>
        <button type="submit" class="btn btn-primary btn-block" data-loading-text="Adding...">Add to basket</button>
    </form>
            </div>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    book = parse_book(soup.find("article", class_="product_pod"))
    assert book.title == "The Invention of Wings"
    assert book.price == "£37.34"
    assert book.available is True


def test_parse_book_missing_title():
    html = """
        <article class="product_pod">
                <div class="image_container">
                        <a href="the-invention-of-wings_448/index.html"><img src="../media/cache/62/fa/62fa1e72f06f05762db5d9cedf654153.jpg" alt="The Invention of Wings" class="thumbnail"></a>
                </div>
                    <p class="star-rating One">
                        <i class="icon-star"></i>
                        <i class="icon-star"></i>
                        <i class="icon-star"></i>
                        <i class="icon-star"></i>
                        <i class="icon-star"></i>
                    </p>

    <div class="product_price">
    <p class="price_color">£37.34</p>
    <p class="instock availability">
        <i class="icon-ok"></i>
            In stock
    </p>
        <form>
            <button type="submit" class="btn btn-primary btn-block" data-loading-text="Adding...">Add to basket</button>
        </form>
                </div>
        </div>
        """
    soup = BeautifulSoup(html, "html.parser")
    with pytest.raises(
        MissingTitleError,
        match="Missing 'h3 a' element for title in the provided document",
    ):
        parse_book(soup.find("article", class_="product_pod"))


def test_parse_book_missing_price():
    html = """
        <article class="product_pod">
                <div class="image_container">
                        <a href="the-invention-of-wings_448/index.html"><img src="../media/cache/62/fa/62fa1e72f06f05762db5d9cedf654153.jpg" alt="The Invention of Wings" class="thumbnail"></a>
                </div>
                    <p class="star-rating One">
                        <i class="icon-star"></i>
                        <i class="icon-star"></i>
                        <i class="icon-star"></i>
                        <i class="icon-star"></i>
                        <i class="icon-star"></i>
                    </p>
     <h3><a href="the-invention-of-wings_448/index.html" title="The Invention of Wings">The Invention of Wings</a></h3>
    <div class="product_price">

    <p class="instock availability">
        <i class="icon-ok"></i>
            In stock
    </p>
        <form>
            <button type="submit" class="btn btn-primary btn-block" data-loading-text="Adding...">Add to basket</button>
        </form>
                </div>
        </div>
        """
    soup = BeautifulSoup(html, "html.parser")
    with pytest.raises(
        MissingPriceError,
        match="Missing '.price_color' element for price in the provided document",
    ):
        parse_book(soup.find("article", class_="product_pod"))


def test_parse_book_missing_title_attribute():
    html = """
        <article class="product_pod">
                <div class="image_container">
                        <a href="the-invention-of-wings_448/index.html"><img src="../media/cache/62/fa/62fa1e72f06f05762db5d9cedf654153.jpg" alt="The Invention of Wings" class="thumbnail"></a>
                </div>
                    <p class="star-rating One">
                        <i class="icon-star"></i>
                        <i class="icon-star"></i>
                        <i class="icon-star"></i>
                        <i class="icon-star"></i>
                        <i class="icon-star"></i>
                    </p>
     <h3><a href="the-invention-of-wings_448/index.html" >The Invention of Wings</a></h3>
    <div class="product_price">
    <p class="price_color">£37.34</p>
    <p class="instock availability">
        <i class="icon-ok"></i>
            In stock
    </p>
        <form>
            <button type="submit" class="btn btn-primary btn-block" data-loading-text="Adding...">Add to basket</button>
        </form>
                </div>
        </div>
        """

    soup = BeautifulSoup(html, "html.parser")

    with pytest.raises(
        MissingTitleError,
        match="Missing 'title' attribute in 'h3 a' element for book title",
    ):
        parse_book(soup.find("article", class_="product_pod"))


def test_parse_book_outofstock():
    html = """
        <article class="product_pod">
                <div class="image_container">
                        <a href="the-invention-of-wings_448/index.html"><img src="../media/cache/62/fa/62fa1e72f06f05762db5d9cedf654153.jpg" alt="The Invention of Wings" class="thumbnail"></a>
                </div>
                    <p class="star-rating One">
                        <i class="icon-star"></i>
                        <i class="icon-star"></i>
                        <i class="icon-star"></i>
                        <i class="icon-star"></i>
                        <i class="icon-star"></i>
                    </p>
     <h3><a href="the-invention-of-wings_448/index.html" title="The Invention of Wings">The Invention of Wings</a></h3>
    <div class="product_price">
    <p class="price_color">£37.34</p>
    <p class="outofstock availability">
        <i class="icon-ok"></i>
            In stock
    </p>
        <form>
            <button type="submit" class="btn btn-primary btn-block" data-loading-text="Adding...">Add to basket</button>
        </form>
                </div>
        </div>
        """
    soup = BeautifulSoup(html, "html.parser")
    book = parse_book(soup.find("article", class_="product_pod"))
    assert book.title == "The Invention of Wings"
    assert book.price == "£37.34"
    assert book.available is False
