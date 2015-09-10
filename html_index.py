# Derived from the dropbox-index project found here:
# http://code.google.com/p/kosciak-misc/wiki/DropboxIndex
#
# Uses icons from famfamfam's "Silk" icon set:
# http://www.famfamfam.com/lab/icons/silk/
#

import os, time, ctypes, argparse
from string import Template

class HtmlIndex:
    format_date = lambda self, date: time.strftime('%Y-%m-%d %H:%M:%S', date)

    file_types = {} # holds an inverted version of file_extensions

    file_extensions = {
        'image':        ('gif', 'jpg', 'jpeg', 'png', 'bmp', 'tif', 'tiff', 'raw', 'img', 'ico'),
        'video':        ('avi', 'ram', 'mpg', 'mpeg', 'mov', 'asf', 'wmv', 'asx', 'ogm', 'vob', '3gp'),
        'music':        ('mp3', 'ogg', 'mpc', 'wav', 'wave', 'flac', 'shn', 'ape', 'mid', 'midi', 'wma', 'rm', 'aac', 'mka'),
        'archive':      ('tar', 'bz2', 'gz', 'arj', 'rar', 'zip', '7z'),
        'package':      ('deb', 'rpm', 'pkg', 'jar', 'war', 'ear'), 
        'pdf':          ('pdf', ),
        'txt':          ('txt', ),
        'markup':       ('html', 'htm', 'xml', 'css', 'rss', 'yaml', 'php', 'php3', 'php4', 'php5'),
        'code':         ('js', 'py', 'pl', 'java', 'c', 'h', 'cpp', 'hpp', 'sql'),
        'font':         ('ttf', 'otf', 'fnt'),
        'document':     ('doc', 'rtf', 'odt', 'abw', 'docx', 'sxw'),
        'spreadsheet':  ('xls', 'ods', 'csv', 'sdc', 'xlsx'),
        'presentation': ('ppt', 'odp', 'pptx'), 
        'application':  ('exe', 'msi', 'bin', 'dmg'),
        'plugin':       ('xpi', ),
        'iso':          ('iso', 'nrg'),
    }

    icons = {
        'img_favicon':      'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAADUUlEQVQ4jV3TTWwUZQDG8f/O7MzsLPsB7C60XaCFFlraWlitabSxgLSQUhJCIvFCgpAYxcQQ5UDUsxqVWOOB6oFa4YQFDFQFTZq0QFdqsLbQD1Bo6kdrQ4txP7o7u7Pzvh4IDfF/f/Kcfi72dwKAooCVg4z1CorixWu2o6sggYIDWesIjshjGh14DBACAPfiOJOF5MKBWGPdZ3m7wNhPt4dYsbQfgESysWJT1SemrnMrPpzDLzrxmSAEbqSEuflqLRg80bavdcuLz1cT9sC7Xq2v7/JQCzqisuHJ3kMvNFPsg4HK4pNdPfGDuen5wxQtG3Vp+zs7aqsqX322IUZ5xMRKJVgV1FgX8XL8TD8D05K9u7ayXMnikXk2lwbJWVl6+n7h6/idzxVV0lJZW0NxxOT+fAJHwkwix4N/05w5soVvj23FsNNMPbCwBfw+m2Bj1GTXczXosEMtVO78dPTGUKli+mMbSktQhE2syODpqAerAIqQNEbd+A0XcxnB6pCPi/E7HPvo/ClLyG0q9ftAyAuTVwZLXeFw7O22NdSENRJZQUFI5jKSggPNaw22lRm81zPGF+1nTxMKHCDgRaWqFdLpN55pbXotuq7KuDSRpXgJ1KzQyBYkQrqoCLnpnbT48FqSjatCBIuXlE/cnCqgqnFV37S3Z8ee3a+3NtUZ6XSe0VmL8ft58o5DQ4lB0oajl1N8/GMKRzg8sVLjUPN6vbwi2jJ4a6rB7VKVgG3lsG3wGAY+PUvIqzI8YxH1KRwfdOgdyfDUBo2Qx8Hr8ZCxIbNgoahKQHWq27omh2+O3/17ttm/PGLaiskyrcD2cpOigM6faYnPr5CyHCIBD6ZY4IPTPyS7z11/ydK1N9243RAJd//x88Qlt6an3np5N4V0jvUhyNoSR0jqS1Rciof6Mi/vn7zA+MDEGspLEiBRAJASokXpqXt/vXPufB9rwxolEQNHgC0gEAxSG1H48qvvGb49c5SyogRSggSVuj0PMakKUlWu3h2513322kQsvNS/entsJb+lDOI3xmg/9U3vr+PTLQT936E+/AVwLWp8lKpAMgPJ7OGmls0n/skKRq+PHMTv68LrWVT4KDf/zxEQ8IJL6bjSP2ZiUCDo73qc8OP9B8ZsWIR07alVAAAAAElFTkSuQmCC',
        'img_back':         'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAEGSURBVDjLpZM/LwRRFMXPspmEaGc1shHRaiXsJ5GIRixbCr6SikxIlqgJM5UohIiGdofovHf/PZVmYwZvTntPfjnn3txWCAFNNFE33L/ZKXYv+1dRgL3r7bu0PbucJp3e4GLjtsrXGq9wkA8SU7tPk87i/MwCzAyP5QNeytcnJl46XMuoNoGKDoVlTkQhJpAgmJqcBjnqkqPTXxN8qz9cD6vdHtQMxXOBt49y5XjzLB/3tau6kWewKiwoRu8jZFvn+U++GgCBlWFBQY4qr1ANcAQxgQaFjwH4TwYrQ5skYBOYKbzjiASOwCrNd2BBwZ4jAcowGJgkAuAZ2dEJhAUqij//wn/1BesSumImTttSAAAAAElFTkSuQmCC',
        'img_dir':          'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAGrSURBVDjLxZO7ihRBFIa/6u0ZW7GHBUV0UQQTZzd3QdhMQxOfwMRXEANBMNQX0MzAzFAwEzHwARbNFDdwEd31Mj3X7a6uOr9BtzNjYjKBJ6nicP7v3KqcJFaxhBVtZUAK8OHlld2st7Xl3DJPVONP+zEUV4HqL5UDYHr5xvuQAjgl/Qs7TzvOOVAjxjlC+ePSwe6DfbVegLVuT4r14eTr6zvA8xSAoBLzx6pvj4l+DZIezuVkG9fY2H7YRQIMZIBwycmzH1/s3F8AapfIPNF3kQk7+kw9PWBy+IZOdg5Ug3mkAATy/t0usovzGeCUWTjCz0B+Sj0ekfdvkZ3abBv+U4GaCtJ1iEm6ANQJ6fEzrG/engcKw/wXQvEKxSEKQxRGKE7Izt+DSiwBJMUSm71rguMYhQKrBygOIRStf4TiFFRBvbRGKiQLWP29yRSHKBTtfdBmHs0BUpgvtgF4yRFR+NUKi0XZcYjCeCG2smkzLAHkbRBmP0/Uk26O5YnUActBp1GsAI+S5nRJJJal5K1aAMrq0d6Tm9uI6zjyf75dAe6tx/SsWeD//o2/Ab6IH3/h25pOAAAAAElFTkSuQmCC',
        'img_file':         'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAQAAAC1+jfqAAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAC4SURBVCjPdZFbDsIgEEWnrsMm7oGGfZrohxvU+Iq1TyjU60Bf1pac4Yc5YS4ZAtGWBMk/drQBOVwJlZrWYkLhsB8UV9K0BUrPGy9cWbng2CtEEUmLGppPjRwpbixUKHBiZRS0p+ZGhvs4irNEvWD8heHpbsyDXznPhYFOyTjJc13olIqzZCHBouE0FRMUjA+s1gTjaRgVFpqRwC8mfoXPPEVPS7LbRaJL2y7bOifRCTEli3U7BMWgLzKlW/CuebZPAAAAAElFTkSuQmCC',
        'img_image':        'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAHwSURBVDjLpZM9a1RBFIafM/fevfcmC7uQjWEjUZKAYBHEVEb/gIWFjVVSWEj6gI0/wt8gprPQykIsTP5BQLAIhBVBzRf52Gw22bk7c8YiZslugggZppuZ55z3nfdICIHrrBhg+ePaa1WZPyk0s+6KWwM1khiyhDcvns4uxQAaZOHJo4nRLMtEJPpnxY6Cd10+fNl4DpwBTqymaZrJ8uoBHfZoyTqTYzvkSRMXlP2jnG8bFYbCXWJGePlsEq8iPQmFA2MijEBhtpis7ZCWftC0LZx3xGnK1ESd741hqqUaqgMeAChgjGDDLqXkgMPTJtZ3KJzDhTZpmtK2OSO5IRB6xvQDRAhOsb5Lx1lOu5ZCHV4B6RLUExvh4s+ZntHhDJAxSqs9TCDBqsc6j0iJdqtMuTROFBkIcllCCGcSytFNfm1tU8k2GRo2pOI43h9ie6tOvTJFbORyDsJFQHKD8fw+P9dWqJZ/I96TdEa5Nb1AOavjVfti0dfB+t4iXhWvyh27y9zEbRRobG7z6fgVeqSoKvB5oIMQEODx7FLvIJo55KS9R7b5ldrDReajpC+Z5z7GAHJFXn1exedVbG36ijwOmJgl0kS7lXtjD0DkLyqc70uPnSuIIwk9QCmWd+9XGnOFDzP/M5xxBInhLYBcd5z/AAZv2pOvFcS/AAAAAElFTkSuQmCC',
        'img_video':        'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAIfSURBVDjLpZNPaBNBGMXfbrubzBqbg4kL0lJLgiVKE/AP6Kl6UUFQNAeDIAjVS08aELx59GQPAREV/4BeiqcqROpRD4pUNCJSS21OgloISWMEZ/aPb6ARdNeTCz92mO+9N9/w7RphGOJ/nsH+olqtvg+CYJR8q9VquThxuVz+oJTKeZ63Uq/XC38E0Jj3ff8+OVupVGLbolkzQw5HOqAxQU4wXWWnZrykmYD0QsgAOJe9hpEUcPr8i0GaJ8n2vs/sL2h8R66TpVfWTdETHWE6GRGKjGiiKNLii5BSLpN7pBHpgMYhMkm8tPUWz3sL2D1wFaY/jvnWcTTaE5DyjMfTT5J0XIAiTRYn3ASwZ1MKbTmN7z+KaHUOYqmb1fcPiNa4kQBuyvWAHYfcHGzDgYcx9NKrwJYHCAyF21JiPWBnXMAQOea6bmn+4ueYGZi8gtymNVobF7BG5prNpjd+eW6X4BSUD0gOdCpzA8MpA/v2v15kl4+pK0emwHSbjJGBlz+vYM1fQeDrYOBTdzOGvDf6EFNr+LYjHbBgsaCLxr+moNQjU2vYhRXpgIUOmSWWnsJRfjlOZhrexgtYDZ/gWbetNRbNs6QT10GJglNk64HMaGgbAkoMo5fiFNy7CKDQUGqE5r38YktxAfSqW7Zt33l66WtkAkACjuNsaLVaDxlw5HdJ/86aYrG4WCgUZD6fX+jv/U0ymfxoWVZomuZyf+8XqfGP49CCrBUAAAAASUVORK5CYII=',
        'img_music':        'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAEzSURBVDjLxdOxasJAHAZwwbfKkjlbJVMpJaYmxtSoNVoSsCLlekQSjcZNRUFFIUNxD5nqY7Rr+wiuX89M3a62lA4f3PL97n/HXQ5A7jfJ/Rng+/1LSsn72UAQ+HlWJp5Hj4Q8gguE4VAIw0GWwSAQWPl1sZhjv39Gr/fAB4bDAJNJhCgaYTweYbNZIY5jrNcruM49HwiCPg6HF6RpiiRJsFwuQQhhYAS7WecD7KzY7bbwPA+UUnS7Xdi2zdZPqNVMPnC6qPl8Cl3XoSgKZFmGJEkwTYOlzAc6HRez2RSu66DRqKNQuIAoigy7hmGU+EC73USr1WDlajayZZkZoqoKm0rlA807S6jeVoRKRRPK5RtB14tvJ8hxbGhaEWc/JLZrXisVKcvxR8AX6Irl4/8+03fzCbreyRfHFw9qAAAAAElFTkSuQmCC',
        'img_archive':      'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAKQSURBVDjLbZNNaJxVFIafe7/5KTPzpUloNK0tIsowCtbiQgRRQReudCMVqYrdiLgQ01UrWUgXXZQumoU2myyKii66dOFCEUo3IiL+VRMFHactYpsMmsy0mbnnx8X8tEn7wuHAudyH97zcG9wdgKWl9zNgl7vvrVar51T1PndHVQHDzBCRFGNhqd1ePXb06PF1gALAhbONF+7PanPtymtP9G2iVK3WmJjYibtjZuNupsWVlYtviaRTwABw4WzjEPDRVGMy/vt3QLpCu73G2toqZoKZE2Mkz3PyfBKxgKplDFUA3rz7wL5Y2lnigdrHiDhuRlaoYJslrv3cWb7cfehka/3BxUY93+EGqolbAU/tqz+K2V/MzFQAHZYQ4146v55v/NPd81UxL6uKQgyY2RgQB025fOUPCC9COAjhJVqt38BlcKpKb/M65kbq9YfB3nQAGOVSxqXWCXDBSZTLBWAAMDOKsYibYURE0naAMjOzC5gc2Pc0vDwApJTQGx3UDJHNLQ7GK1xq/Q7hFQivQjzMn82LY4CqhiwWw8BBQNW2OxBK5Yxm812whNNnx5YVtBBkoxICkLqYbcugt9Fh9+xj4/RHtblxA7EMVZsOYZC+qqMqWwBHfvr829OjgRNIWkIsIhb54cr+r7Ms+3Bqanr0GjHzm4AnDy8vAAujwfz83NTs7O7z3W7nYTOjH3uPp7RuWZYNHdhtDrZIVda/8+fPWa06nfWvfjJxdfFTEd2zvPzLZyn1CCHSrx954/UPWi8DC2H0G2/VM8ebzeceqd375fer/9WvnTgDVET0oLsWzJDmPe/lzx64K//ix43WHQH1t1fmgLkC/TNPy8lFM4vuWhGx6G72TXX+UAqVd4DT/wMfm3vSJoP5ygAAAABJRU5ErkJggg==',
        'img_package':      'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAALnSURBVDjLfZNLaFx1HIW/e2fuzJ00w0ymkpQpiUKfMT7SblzU4kayELEptRChUEFEqKALUaRUV2YhlCLYjYq4FBeuiqZgC6FIQzBpEGpDkzHNs5PMTJtmHnfu6//7uSh2IYNnffg23zmWqtIpd395YwiRL1Q0qyIfD56cmOvUs/4LWJg40auiH6jI+7v3ncybdo2Hy9ebKvqNGrn03Nj1+x0Bi1dHHVV9W0U+ye4d2d83+Ca2GJrlGZx0gkppkkfrsysqclFFvh8++3v7CWDh6ugIohfSPcPH+w6fwu05ABoSby9yb3Kc/mePYXc9TdCqslWapVGdn1Zjxo++O33Fujtx4gdEzj61f8xyC8/jN2rsVOcxYZOoVSZtBewZOAT+NonuAWw3S728wFZpFm975cekGjlz8NXLVtSo0SxPImGdtFfFq5epr21wdOxrnMwuaC2jrRJWfYHdxRfIFeDWr0unkyrSUqxcyk2TLQzQrt6hqydPvidDBg/8VTAp8DegvYa3OU1z+SbuM6dQI62kioAAVgondwAnncWvzCDNCk4CLO9vsJVw8xqN+iPiTB5SaTSKURGSaoTHHgxoAMlduL1HiFMZXP8BsvkbO1GD2O3GpLOIF0KsSBijxmCrMY+FqgGJQDzQgGT3XrJ7DuI5EKZd4iDG+CHG84m8AIki1Ai2imRsx4FEBtQHCUB8MG1wi8QKGhjEC4mbAVHTx8kNYSuoiGurkRtLN76ivb0K6SIkusCEoBEgaCQYPyT2QhKpAXKHTiMmQ2lmChWZTrw32v9TsLOyVlu8Nhi2G4Vs32HsTC9IA2KPRuU2Erp097+O5RRYvz3H1r3JldivfY7IR0+mfOu7l3pV5EM1cq744mi+OPwaRD71tSk0Vsp3/uLB6s2minyrIpeOf7a00fFMf1w+MqRGzqvIW/teecdqV5a5P/8ncXv9ZxUdf/lCae5/3/hvpi4OjajIp4ikVOTLY+cXr3Tq/QPcssKNXib9yAAAAABJRU5ErkJggg==',
        'img_pdf':          'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAHhSURBVDjLjZPLSxtRFIfVZRdWi0oFBf+BrhRx5dKVYKG4tLhRqlgXPmIVJQiC60JCCZYqFHQh7rrQlUK7aVUUfCBRG5RkJpNkkswrM5NEf73n6gxpHujAB/fOvefjnHM5VQCqCPa1MNoZnU/Qxqhx4woE7ZZlpXO53F0+n0c52Dl8Pt/nQkmhoJOCdUWBsvQJ2u4ODMOAwvapVAqSJHGJKIrw+/2uxAmuJgFdMDUVincSxvEBTNOEpmlIp9OIxWJckMlkoOs6AoHAg6RYYNs2kp4RqOvfuIACVFVFPB4vKYn3pFjAykDSOwVta52vqW6nlEQiwTMRBKGygIh9GEDCMwZH6EgoE+qHLMuVBdbfKwjv3yE6Ogjz/PQ/CZVDPSFRRYE4/RHy1y8wry8RGWGSqyC/nM1meX9IQpQV2JKIUH8vrEgYmeAFwuPDCHa9QehtD26HBhCZnYC8ucGzKSsIL8wgsjiH1PYPxL+vQvm5B/3sBMLyIm7GhhCe90BaWykV/Gp+VR9oqPVe9vfBTsruM1HtBKVPmFIUNusBrV3B4ev6bsbyXlPdkbr/u+StHUkxruBPY+0KY8f38oWX/byvNAdluHNLeOxDB+uyQQfPCWZ3NT69BYJWkjxjnB1o9Fv/ASQ5s+ABz8i2AAAAAElFTkSuQmCC',
        'img_txt':          'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAQAAAC1+jfqAAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAADoSURBVBgZBcExblNBGAbA2ceegTRBuIKOgiihSZNTcC5LUHAihNJR0kGKCDcYJY6D3/77MdOinTvzAgCw8ysThIvn/VojIyMjIyPP+bS1sUQIV2s95pBDDvmbP/mdkft83tpYguZq5Jh/OeaYh+yzy8hTHvNlaxNNczm+la9OTlar1UdA/+C2A4trRCnD3jS8BB1obq2Gk6GU6QbQAS4BUaYSQAf4bhhKKTFdAzrAOwAxEUAH+KEM01SY3gM6wBsEAQB0gJ+maZoC3gI6iPYaAIBJsiRmHU0AALOeFC3aK2cWAACUXe7+AwO0lc9eTHYTAAAAAElFTkSuQmCC',
        'img_markup':       'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAHtSURBVDjLjZM9T9tQFIYpQ5eOMBKlW6eWIQipa8RfQKQghEAKqZgKFQgmFn5AWyVDCipVQZC2EqBWlEqdO2RCpAssQBRsx1+1ndix8wFvfW6wcUhQsfTI0j33PD7n+N4uAF2E+/S5RFwG/8Njl24/LyCIOI6j1+v1y0ajgU64cSSTybdBSVAwSMmmacKyLB/DMKBpGkRRZBJBEJBKpXyJl/yABLTBtm1Uq1X2JsrlMnRdhyRJTFCpVEAfSafTTUlQoFs1luxBAkoolUqQZbmtJTYTT/AoHInOfpcwtVtkwcSBgrkDGYph+60oisIq4Xm+VfB0+U/P0Lvj3NwPGfHPTcHMvoyFXwpe7UmQtAqTUCU0D1VVbwTPVk5jY19Fe3ZfQny7CE51WJDXqpjeEUHr45ki9rIqa4dmQiJfMLItGEs/FcQ2ucbRmdnSYy5vYWyLx/w3EaMfLmBaDpMQvuDJ65PY8Dpnz3wpYmLtApzcrIAqmfrEgdZH1grY/a36w6Xz0DKD8ES25/niYS6+wWE8mWfByY8cXmYEJFYLkHUHtVqNQcltAvoLD3v7o/FUHsNvzlnwxfsCEukC/ho3yUHaBN5Buo17Ojtyl+DqrnvQgUtfcC0ZcAdkUeA+ye7eMru9AUGIJPe4zh509UP/AAfNypi8oj/mAAAAAElFTkSuQmCC',
        'img_code':         'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAHdSURBVDjLjZNPaxNBGIdrLwURLznWgkcvIrQhRw9FGgy01IY0TVsQ0q6GFkT0kwjJId9AP4AHP4Q9FO2hJ7El2+yf7OzMbja7Sf0578QdNybFLjwszLu/Z2femZkDMEfI54FkRVL4Dw8l8zqXEawMBgM2HA6vR6MRZiHraDabH7KSrKBA4SAIEIahxvd9eJ6HbrerJKZpotVqaUkavkMC+iCKIsRxrN6EEAKMMViWpQT9fh/0k3a7PZZkBUPmqXAKCSjAOYdt21NLUj1JBYW7C6vi6BC8vKWKQXUXQcNA5Nh6KY7jqJl0Op1JwY/Hi7mLp/lT/uoA/OX2WLC3C9FoQBwfILKulIRmQv1wXfevwHmyuMPXS5Fv1MHrFSTmhSomnUvw/Spo3C+vg3/+pJZDPSGRFvilNV+8PUZvoziKvn+d3LZvJ/BelMDevIZXK2EQCiUhtMDM53bY5rOIGXtwjU3EVz/HM5Az8eplqPFKEfzLR91cOg8TPTgr3MudFx+d9owK7KMNVfQOtyQ1OO9qiHsWkiRRUHhKQLuwfH9+1XpfhVVfU0V3//k4zFwdzjIlSA/Sv8jTOZObBL9uugczuNaCP5K8bFBIhduE5bdC3d6MYIkkt7jOKXT1l34DkIu9e0agZjoAAAAASUVORK5CYII=',
        'img_font':         'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAHJSURBVDjLY/j//z8DJZiBZgY4tN9wcO6+0erZd2uKc+fNfoeWGxMcW27Msiq+3GWUdIZXL/okI14D7JqvB+csf3Rv4p6X//t3Pf/fvf35/8Ilj3471V3bph9zmougC6xrr8mETbu7q3jl40/FKx5+LVzy8Ltd+eUZBvGnOYjygk3llfKCZY++u3fcWutcd21B07on/61yz88kKgwsCi8qJc++9yhu2p37ppnnQ4C4oWblo/9WOReXEjTANOsCs1PD9VVZ8+9/N0k7m6Yfe5LLOPFMR+Wyh/9dqq5eUvc6xIbXALOs8zEZc+9/C+q+ddEw/rSfXuRxLfP0swuqgAYEt934pOq2nxenAUbJZ0TjJt9+Vbn80X+v5huXrbLOb7LMOLfVterqjcYVj/+Htd38qey4TxqrAQaxpxntSy7PBvnVPO0MSmCZJ5/ZWL7g/v+ozlv/lex2K2EYoB9zigsYPS6lSx7+j+i59UYn6JgtTIGK635hdY/D9dnT7vxP6L/9X9F+b4icxTYmFAMsMs6ti+2/9S9hwu3/Ac3X32oHHOlVdtoroGS/R0vb9/Aip8ILrwLrrv33rbn63zD02F5Zy22GtM8LdDMAACVPr6ZjGHxnAAAAAElFTkSuQmCC',
        'img_document':     'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAIdSURBVDjLjZO7a5RREMV/9/F9yaLBzQY3CC7EpBGxU2O0EBG0sxHBUitTWYitYCsiiJL0NvlfgoWSRpGA4IMsm43ZXchmv8e9MxZZN1GD5MCBW8yce4aZY1QVAGPMaWAacPwfm8A3VRUAVJWhyIUsy7plWcYQgh7GLMt0aWnpNTADWFX9Q2C+LMu4s7Oj/X5/xF6vp51OR1utloYQtNls6vLy8kjE3Huz9qPIQjcUg/GZenVOokIEiSBBCKUSQ+TFwwa1Wo2iKBARVlZW3iwuLr7izssPnwZ50DLIoWz9zPT+s/fabrf/GQmY97GIIXGWp28/08si5+oV1jcGTCSO6nHH2pddYqmkaUq320VECCFQr9cBsBIVBbJcSdXQmK7Q6Qsnq54sj2gBplS896RpSpIkjI2NjVZitdh7jAOSK6trXcpC2GjlfP1esHD+GDYozjm893jvSZJkXyAWe+ssc6W5G9naLqkaw/pGxBrl1tVpJCrWWpxzI6GRgOQKCv2BYHPl5uUatROeSsVy7eIkU9UUiYoxBgDnHNbagw4U6yAWwpmphNvXT6HAhAZuLNRx1iDDWzHG/L6ZEbyJVLa2c54/PgsKgyzw5MHcqKC9nROK/aaDvwN4KYS7j959DHk2PtuYnBUBFUEVVBQRgzX7I/wNM7RmgEshhFXAcDSI9/6KHQZKAYkxDgA5SnOMcReI5kCcG8M42yM6iMDmL261eaOOnqrOAAAAAElFTkSuQmCC',
        'img_spreadsheet':  'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAIpSURBVDjLjZNPSFRRFMZ/9707o0SOOshM0x/JFtUmisKBooVEEUThsgi3KS0CN0G2lagWEYkSUdsRWgSFG9sVFAW1EIwQqRZiiDOZY804b967954249hUpB98y/PjO5zzKREBQCm1E0gDPv9XHpgTEQeAiFCDHAmCoBhFkTXGyL8cBIGMjo7eA3YDnog0ALJRFNlSqSTlcrnulZUVWV5elsXFRTHGyMLCgoyNjdUhanCyV9ayOSeIdTgnOCtY43DWYY3j9ulxkskkYRjinCOXy40MDAzcZXCyVzZS38MeKRQKf60EZPXSXInL9y+wLZMkCMs0RR28mJ2grSWJEo+lH9/IpNPE43GKxSLOOYwxpFIpAPTWjiaOtZ+gLdFKlJlD8u00xWP8lO/M5+e5efEB18b70VqjlMJai++vH8qLqoa+nn4+fJmiNNPCvMzQnIjzZuo1V88Ns3/HAcKKwfd9tNZorYnFYuuAMLDMfJ3m+fQznr7L0Vk9zGpLmezB4zx++YggqhAFEZ7n4ft+HVQHVMoB5++cJNWaRrQwMjHM9qCLTFcnJJq59WSIMLAopQDwfR/P8+oAbaqWK2eGSGxpxVrDnvQ+3s++4tPnj4SewYscUdUgIiilcM41/uXZG9kNz9h9aa+EYdjg+hnDwHDq+iGsaXwcZ6XhsdZW+FOqFk0B3caYt4Bic3Ja66NerVACOGttBXCbGbbWrgJW/VbnXbU6e5tMYIH8L54Xq0cq018+AAAAAElFTkSuQmCC',
        'img_presentation': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAHeSURBVDjLjZO/i1NBEMc/u+/lBYxiLkgU7vRstLEUDyxtxV68ykIMWlocaGHrD1DxSAqxNf4t115jo6DYhCRCEsk733s7u2PxkuiRoBkYdmGZz3xndsaoKgDGmC3gLBDxbxsA31U1AKCqzCBXsywbO+e8iOgqz7JM2+32W+AiYFX1GGDHOeen06mmabrwyWSio9FI+/2+ioj2ej3tdDoLiJm+bimAhgBeUe9RmbkrT5wgT97RaDQoioIQAt1ud7/Var1h+uq+/s9+PLilw+FwqSRgJ1YpexHSKenHF4DFf/uC3b7CydsPsafraO5IkoTxeEwIARGh2WwCYNUJAOmHZ5y4eY/a7h4hPcIdHvDz/fMSnjviOCZJEiqVCtVqdfEl8RygHkz9DLZWQzOHisd9OizfckcURRhjMMbMm14CQlEC/NfPjPd2CSJQCEEEDWYBsNZijFkaCqu5Ky+blwl5geaOUDg0c8TnNssSClkER1GEtXYZcOruI6ILl1AJqATirW02Hr8sFThBVZfklyXMFdQbbDzdXzm78z4Bx7KXTcwdgzs3yizuzxAhHvVh4avqBzAzaQa4JiIHgGE9C3EcX7ezhVIgeO9/AWGdYO/9EeDNX+t8frbOdk0FHhj8BvUsfP0TH5dOAAAAAElFTkSuQmCC',
        'img_application':  'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAE8SURBVDjLpVM9SwNREJzTpx4JaGMn/oJrRMtU/g2xsLD1F/gDbK0lpaAgNmJnI1YWasBOELs0QgQDfsQ4Mxb3vEvgipwuLAsLszszb19iG/+JsHf6dDU3g9WXdzdtABIsAQZowjJkwSRkwyQoYX52+PYx8F0w0FrPFqfuuwP0P1W5ZW2hi9vXpViXsXOyieOtw+b1zUMr2T16tGnYBizYhqR8a2QjquxRkAjJsIhgGhsrg4q9CYDpmGWMerZ//oxgC1mW/clAnl0gIE6UqvXbLlIqJTYaDeibCBRrAX97ACAKwXIt4KgHEhEUGdQBlgOE4Khd0sTAMQZkzoDkxMBiAI1g5gzSNK39jJYQJKHT6SBN00KGpDFGVfJ6vR5kIyQetg8uh9tiH+IIMNb8hPOzNV2cuATAX+3kv9/5B7T5iPkmloFJAAAAAElFTkSuQmCC',
        'img_plugin':       'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAHhSURBVDjLpZI9SJVxFMZ/r2YFflw/kcQsiJt5b1ije0tDtbQ3GtFQYwVNFbQ1ujRFa1MUJKQ4VhYqd7K4gopK3UIly+57nnMaXjHjqotnOfDnnOd/nt85SURwkDi02+ODqbsldxUlD0mvHw09ubSXQF1t8512nGJ/Uz/5lnxi0tB+E9QI3D//+EfVqhtppGxUNzCzmf0Ekojg4fS9cBeSoyzHQNuZxNyYXp5ZM5Mk1ZkZT688b6thIBenG/N4OB5B4InciYBCVyGnEBHO+/LH3SFKQuF4OEs/51ndXMXC8Ajqknrcg1O5PGa2h4CJUqVES0OO7sYevv2qoFBmJ/4gF4boaOrg6rPLYWaYiVfDo0my8w5uj12PQleB0vcp5I6HsHAUoqUhR29zH+5B4IxNTvDmxljy3x2YCYUwZVlbzXJh9UKeQY6t2m0Lt94Oh5loPdqK3EkjzZi4MM/Y9Db3MTv/mYWVxaqkw9IOATNR7B5ABHPrZQrtg9sb8XDKa1+QOwsri4zeHD9SAzE1wxBTXz9xtvMc5ZU5lirLSKIz18nJnhOZjb22YKkhd4odg5icpcoyL669TAAujlyIvmPHSWXY1ti1AmZ8mJ3ElP1ips1/YM3H300g+W+51nc95YPEX8fEbdA2ReVYAAAAAElFTkSuQmCC',
        'img_iso':          'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAIzSURBVDjLhZNbbtpQEIazgaygG4nUjXRH3QAySvvSKokEgeaBSBGFXJqAQkMxYCA03EJMzcWxCb6AAYP9d46BhqRURfqw5Zn5z5y5bAHYWufd++hbwkdkCYUYEBXCz2yv/dcDtwmOsL/yIkotHU11irY5g9QfIp5tgdmWPtsvBJbB0YOLCuaOC0kHjtIGvhQMfO9PMSYnh2A25sN8VyIrAY4ZNBvezyTvvUsNn66fIGgOXPpGD+jOwr4U4TwBetkhHLFvYy+loqounE74MfxnKupDeBn06M+k55ThukzAYbHe6TG630lBx8dLBbsXCooSUOsBqapJ15mgPwFkEtAplcEcMIjYoiYcE8gLoobPyUcSkOH/JiOS1XGYqDOHLiOcbMCkoDZlU30ChPYcgqgze54JqLfSiE6WsUvBH0jkpmEyY4d4s6RT6U0QoaKGMppHUbKYj/pHwH8ugzvtwXfaRfr+b4HiLwshXsf+zYDoo7AmkM8/DMCdd73gIKlXVRcs7dUVDhMNJBssgyGOSxai5RFyzecreEW8vh9DkIGWBTQMQgMqjxOUOhOkmjOEciPs02wEMiYSJLZeRK+NNrVGph7dDQC+C1yJQLw+x/HtFOG8hQBv4eCHiSBvkrD93Mb1QVKoXYICJCg4VnMRKc8QFsYIZhfBAd5AWrRfDtLrUZYMFznKIF6bI1JcnH4k0C7cWfgp25tHedMyZR90lLtTrwYZKgj79s9l+s86K8t336Z1/g2YLh6PHfCmogAAAABJRU5ErkJggg==',
        'img_asc':          'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAAZiS0dEAP8A/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9oCFBEdCtiXSgQAAAAIdEVYdENvbW1lbnQA9syWvwAAAFlJREFUOMtjYMAPuKCYbLAUiskG/6EYJ2BioBAMMwP+MzAw9BOhpx9XwMJCfAaeWFiDLsaIxRBiACMuA4gxhBEnhwhDGAkK4DGEkSZJmYWAAcUMDAxvGGgJAHeDFSaZyU9WAAAAAElFTkSuQmCC',
        'img_desc':         'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAAZiS0dEAP8A/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9oCFBEcOX5cGlMAAAAIdEVYdENvbW1lbnQA9syWvwAAAF9JREFUOMtjYKAxiGNgYCiixID/UIwTMBLQTFAtI5GacapnJEEzVj2MJGrG0MeERfNaqAJGNA2MDAwMM/FZ9J+BgaGfiFjoJ8GlhKORidKUNgwMYCEgv4xSC7igGCcAAI4dEfsaMSZ6AAAAAElFTkSuQmCC',
    }

    page_template = Template(
        '<!DOCTYPE HTML>'
        '<html lang="en">'
            '<head>'
                '<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>'
                '<meta name="robots" content="${robots}">'
                '<title>${title}</title>'
                '<link rel="shortcut icon" href="${img_favicon}"/>'
                '<style>'
                    'body{font-family:Verdana,sans-serif;font-size:12px}'
                    'a{text-decoration:none;color:#00A}'
                    'a:hover{text-decoration:underline}'
                    '#html-index-header{padding:0;margin:.5em auto .5em 1em}'
                    'table#html-index-list{text-align:center;margin:0 auto 0 1.5em;border-collapse:collapse}'
                    '#html-index-list tbody,#html-index-list thead{border-bottom:1px solid #555}'
                    '#html-index-list th:hover{cursor:pointer;cursor:hand;background-color:#EEE}'
                    '#direction{border:0;vertical-align:bottom;margin:0 .5em}'
                    '#html-index-dir-info,#html-index-footer{margin:1em auto .5em 2em}'
                    '#html-index-list tr,th{line-height:1.7em;min-height:25px}'
                    '#html-index-list tbody tr:hover{background-color:#EEE}'
                    '.name{text-align:left;width:35em}'
                    '.date,.size{text-align:right;padding-right:1em}'
                    '.name a,thead .name{padding-left:22px}'
                    '.name a{display:block}.size{width:7em}'
                    '.date{width:15em}'
                    '#html-index-footer{font-size:smaller}'
                    '.back,.dir,.file{background-repeat:no-repeat;background-position:2px 4px}'
                    '.back{background-image:url(${img_back});}'
                    '.dir{background-image:url(${img_dir});}'
                    '.file{background-image:url(${img_file});}'
                    '.image{background-image:url(${img_image});}'
                    '.video{background-image:url(${img_video});}'
                    '.music{background-image:url(${img_music});}'
                    '.archive{background-image:url(${img_archive});}'
                    '.package{background-image:url(${img_package});}'
                    '.pdf{background-image:url(${img_pdf});}'
                    '.txt{background-image:url(${img_txt});}'
                    '.markup{background-image:url(${img_markup});}'
                    '.code{background-image:url(${img_code});}'
                    '.font{background-image:url(${img_font});}'
                    '.document{background-image:url(${img_document});}'
                    '.spreadsheet{background-image:url(${img_spreadsheet});}'
                    '.presentation{background-image:url(${img_presentation});}'
                    '.application{background-image:url(${img_application});}'
                    '.plugin{background-image:url(${img_plugin});}'
                    '.iso{background-image:url(${img_iso});}'
                '</style>'
                '<script type="text/javascript" src="//ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js"></script>'
                '<script>'
                    'function sort() {'
                        'column = $(this).attr("class").split(" ")[0];'
                        '$("#direction").remove();'
                        'if ($(this).hasClass("desc")) {'
                            '$("#html-index-list thead tr th").each(function(i) { $(this).removeClass("asc").removeClass("desc") });'
                            '$(this).addClass("asc");'
                            'reverse = -1;'
                        '} else {'
                            '$("#html-index-list thead tr th").each(function(i) { $(this).removeClass("asc").removeClass("desc") });'
                            '$(this).addClass("desc");'
                            'reverse = 1;'
                        '}'
                        'var sort_img = "<img src=\\""+(reverse == 1 ? "${img_desc}" : "${img_asc}")+"\\" id=\\"direction\\" />";'
                        'if (column == "name") {'
                            '$(this).append(sort_img);'
                        '} else {'
                            '$(this).prepend(sort_img);'
                        '}'
                        'rows = $("#html-index-list tbody tr").detach();'
                        'rows.sort(function(a, b) {'
                            'result = $(a).data("type") - $(b).data("type");'
                            'if (result != 0) { return result; }'
                            'return (($(a).data(column) < $(b).data(column)) - ($(a).data(column) > $(b).data(column))) * reverse;'
                        '});'
                        '$("#html-index-list tbody").append(rows);'
                    '}'
                    'function prepare() {'
                        '$("#html-index-list tbody tr").each(function(i) {'
                            'if ($(this).children(".name").hasClass("back")) {'
                               ' $(this).data("type", 1);'
                            '} else if ($(this).children(".name").hasClass("dir")) {'
                                '$(this).data("type", 2);'
                            '} else {'
                                '$(this).data("type", 3);'
                            '}'
                            '$(this).data("name", $(this).children(".name").text().toLowerCase());'
                            '$(this).data("size", parseInt($(this).children(".size").attr("sort")));'
                            '$(this).data("date", parseInt($(this).children(".date").attr("sort")));'
                        '});'
                        '$("#html-index-list thead tr th").each(function(i) {'
                            '$(this).bind("click", sort);'
                        '});'
                    '}'
                    '$(document).ready(function(){'
                        'prepare();'
                    '});'
                '</script>'
            '</head>'
            '<body>'
                '<h1 id="html-index-header">${title}</h1>'
                '<table id="html-index-list">'
                    '<thead>'
                        '<tr>'
                            '<th class="name">Name</th>'
                            '<th class="size">Size</th>'
                            '<th class="date">Last Modified</th>'
                        '</tr>'
                    '</thead>'
                    '<tbody>'
                        '${table_content}'
                    '</tbody>'
                '</table>'
                '<div id="html-index-footer">'
                    'Generated on <strong>${generation_date}</strong>'
                '</div>'
            '</body>'
        '</html>'
    )

    back_template = (
        '<tr>'
            '<td class="name back">'
                '<a href="../index.html">..</a>'
            '</td>'
            '<td class="size">'
                '&nbsp;'
            '</td>'
            '<td class="date">'
                '&nbsp;'
            '</td>'
        '</tr>'
    )

    dir_template = Template(
        '<tr>'
            '<td class="name dir">'
                '<a href="${name}/index.html">${name}</a>'
            '</td>'
            '<td class="size">'
                '&nbsp;'
            '</td>'
            '<td class="date" sort="${time_abs}">'
                '${time}'
            '</td>'
        '</tr>'
    )

    file_template = Template(
        '<tr>'
            '<td class="name file ${type}">'
                '<a href="${name}">${name}</a>'
            '</td>'
            '<td class="size" sort="${size_abs}">'
                '${size}'
            '</td>'
            '<td class="date" sort="${time_abs}">'
                '${time}'
            '</td>'
        '</tr>'
    )

    def __init__(self):
        for type, extensions in self.file_extensions.items():
            self.file_types.update(dict.fromkeys(extensions, type))

    def from_command_line(self):
        parser = argparse.ArgumentParser(
            description = 'Creates an index.html file which lists the contents of the directory',
            epilog = 'This tool will overwrite any existing index.html file(s)'
        )

        parser.add_argument(
            '-R', '-r', '--recursive',
            action = 'store_true',
            default = False,
            help = 'Include subdirectories [default: %(default)s]'
        )

        parser.add_argument(
            '-S', '-s', '--searchable',
            action = 'store_true',
            default = False,
            help = 'Allow created page to be listed by search engines [default: %(default)s]'
        )

        parser.add_argument(
            'directory',
            nargs = '?',
            default = '.',
            help = 'The directory to process [default: %(default)s]'
        )

        args = parser.parse_args()

        self.build_index(args.directory, args.recursive, args.searchable)

    def build_index(self, path, recursive = False, searchable = False, parent = None):
        if not os.path.isdir(path):
            print('ERROR: Directory {} does not exist'.format(path))
            return False

        contents = [os.path.join(path, file) for file in os.listdir(path) if file != 'index.html']
        contents = [file for file in contents if not self.is_hidden(file)]

        files = [file for file in contents if os.path.isfile(file)]
        files.sort(key = str.lower)

        if recursive:
            dirs = [file for file in contents if os.path.isdir(file)]
            dirs.sort(key = str.lower)
        else:
            dirs = []

        index_file = open(os.path.join(path, 'index.html'), 'w')
        index_file.write(self.build_html(path, parent, dirs, files, searchable))
        index_file.close()

        print('Created index.html for ' + os.path.realpath(path))

        for dir in dirs:
            self.build_index(dir, recursive, searchable, path)

        return True

    def is_hidden(self, filepath):
        filename = os.path.basename(os.path.abspath(filepath))
        return filename.startswith('.') or self.has_hidden_attribute(filepath)

    def has_hidden_attribute(self, filepath):
        try:
            attrs = ctypes.windll.kernel32.GetFileAttributesW(filepath)
            if attrs == -1:
                return False

            return bool(attrs & 2)

        except (AttributeError):
            return False

    def build_html(self, path, parent, dirs, files, searchable):
        table_content = ''

        if parent:
            table_content += self.back_template

        for dir in dirs:
            table_content += self.dir_template.safe_substitute({
                'name': os.path.basename(dir),
                'time': self.format_date(time.localtime(os.path.getmtime(dir))),
                'time_abs': os.path.getmtime(dir),
            })

        for file in files:
            table_content += self.file_template.safe_substitute({
                'name': os.path.basename(file),
                'type': self.get_filetype(os.path.basename(file)),
                'size': self.get_readable_size(file),
                'size_abs': os.path.getsize(file),
                'time': self.format_date(time.localtime(os.path.getmtime(file))),
                'time_abs': os.path.getmtime(file),
            })

        return self.page_template.safe_substitute(dict(self.icons, 
            robots = not searchable and 'noindex, nofollow' or '',
            title = os.path.basename(os.path.realpath(path)),
            table_content = table_content,
            generation_date = self.format_date(time.localtime()),
        ))

    def get_filetype(self, file_name):
        extension = file_name.rsplit('.', 1)[-1].lower()
        return self.file_types.get(extension, '')

    def get_readable_size(self, file):
        size = os.path.getsize(file)

        for unit in ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']:
            if abs(size) < 1024.0:
                return '{:3.1f} {}'.format(size, unit)

            size /= 1024.0

        return '{:3.1f} YB'.format(size)

if __name__ == '__main__':
    HtmlIndex().from_command_line()
