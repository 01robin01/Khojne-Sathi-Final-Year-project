$(function () {
  if ($('.product-slider').length) {
    $('.product-slider').slick({
      slidesToShow: 4,
      slidesToScroll: 4,
      arrows: true,
      dots: false,
      responsive: [
        {
          breakpoint: 992,
          settings: {
            slidesToShow: 2,
            slidesToScroll: 2
          }
        },
        {
          breakpoint: 576,
          settings: {
            slidesToShow: 1,
            slidesToScroll: 1
          }
        }
      ]
    });
  }
});
