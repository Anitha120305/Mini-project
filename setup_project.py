"""
Creates the whole Expense Tracker project.

How to use:
  1. Put this file anywhere (for example your Desktop or "mini folder").
  2. Run:   python setup_project.py
  3. A folder called  expense_tracker  appears next to this file.
  4. Open that folder in VS Code, then run:
        python check.py
        python app.py
"""
import base64
import os
import zlib

FILES = {
    'app.py':
        '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',
    'check.py':
        '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',
    'static/app.css':
        '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',
    'static/style.css':
        'eNqVVNGOmzAQfOcrLJ0qtdVxAg5IxD31U4xtwD1jI9tcklb99y5gDASiXpMoCrv27OzMbr6j3wGCV6muoeG/uKwL+K0p0yGE3sZc'
        'i3XNZYGi6bHDlI7n4PlPEASlojeHUilpwwq3XNwK9ENzLJ6RwdKEhmlevQVTKUzea616SQv0VKVVXp1dpuUybBivG1ugOIo+Ghen'
        '3HQCA2Ql2NXFfvbG8uoWEijJJFwg8M20y2LBaxlyy1qzZAayL8N5zCXTjvKFU9uM5b7MLPA1dNE0i7q5oG87GWMTGNZ0FnDV1aWB'
        'yvfXXjMP5QTWmPIe+MXrDNjQYKouIC+C+FgN6brEX6Nn5D4v8beJQBO76pZdbTg2fSfE5B14aa1qhzZ9qdErsJxBR/ncUZP8J+D5'
        'EC/xCpm+tNwK9i9YooTSMA+n0+m4UJLNmAKXTDg8PxmlUOT9+OZpS/HiBqxUgk6AXHa9fTgO3sA48UD3qp7vrIUQuGaU4BQ9EUKO'
        'fT/ULvZ9jrSKSpHeOHKqtwJGt0BSSbbFnPXLssxtZQ/c5Ce6et1x36PvGW+WOEmSrY3rBVj3lvv7pNdmONkpviznxLlo1Idfz02d'
        'NE3dWLXMGFyzo0NVPLx3bUYPzXu4lwvbh2O7bi71Qz9Bh8OtT66TVd38x7JZhzzPJ0zsgObEIvnBUC8lKSNKY8tBVWfrCLaReHcQ'
        'dGR6GLTh9F9GnsL7',
    'templates/base.html':
        'eNqNVE2L2zAQvedXTA3BCSTr9taDFWi7W3ootJT0sJRiJtbEFlFkIylJQ/B/71i2Uyf0EF/s+XhPb0YzTt88f/u0fv3+AqXf69Uk'
        'bV+g0RQiIhO1DkK5mgA/6Z48Ql6ideRF9HP9efk+GocM7klER0WnurI+grwyngynnpT0pZB0VDktg7EAZZRXqJcuR03i3dPbgcor'
        'r2l1mcJGV/kOggnT5uVPTcYRrC3mO7IcJyO7lGmTJh2qY9DK7MCSFpHzZ02uJGI1paWtiC4XOFidbSs7i51Hr/J4AVulKYiPsa6f'
        'cufiOTRNW33SlZ9uKnleTTp6g0fINTonIv7coO2Vh6Cr0QzRjUUjo9Wd8jRpc0YQqcZ8y1a9G1GGHPyPfImu3FRoZa/2ebDTBB+A'
        'o5QZddJ6gg9SQu95jKJUzlf23MO/dNZj0M1BFuR75MdgPAa01A7XcEM/OusxqK6K6jCc+TUYMOMER86pyvyKD45s1g5C/Jtz5jes'
        'acL31A9Ywvc0TMMe1fXCaywo6gPtw0N6Ur6EPR/AIQcCuM5sy9klyWxwz9qkLEdPRWUVOeHtgeY81jclMRlXAX3aeTGw8ib9O+AO'
        'cz9f4WTgkuPwtTyhNcoUMajtlRiEgPgaIM2TG8ehZYwbzmyaUT9GCnknW5EjGZ0ztIG9Y3e3vP1PgoO3K923N2n7yy1Nk24FeSPD'
        'j+ovq7Ft0g==',
    'templates/budget.html':
        'eNqtV9tu4zYQfc9XDFi4toFYTjco0O3aKrbpolgg3RSb9GFRFAYl0ZIaihRIyo2R5qV/1d/pl3RISrYly84F0YvNETmXMzOHo/sB'
        'sDvDRKKBRFSzIDMFJzB4OLkfQMRlfAsmN5yh5McqSZmBCXy4K5nQDG4UjW+Zwo143u/Fc9uDsRSo2TjhLHsTfhSxLBh8DZHTpGdT'
        'FOKrJF9BzKnWc1JSwTgJTwCf2VKqAgpmMpnMya9X1zcEaGxyKebk/h4qxRe4YzT02oZjeHjAk+6oO56dh19kpaCQgq3R1vnuyx2b'
        '1swkVXlS293d05Y4KacR44CH5iR3AZHwFww042vwa5iCppyqNYz+++ff8WzqTvRoykVZGTDrks2JqIqIKQJ5slELghZsu9KGlXNy'
        'Fpx9Q6DIEYMzsqeyflaUV8yBNBwEb5bDv22I1Iy8qjHky8ZVxjGPw6GFDkpOY5ZJnjAMjQVpAOdn+HRRme7B8jhQmq5ykWoSXlRK'
        '2ZKoBS9FqNFXQ7RZvgJGtS4HUuPlcZS+fSWQKGfKLEqmYkSIhO/tEssf/sqYAAoxNSyVWFWK0ThjiN3gBci1jdT4dYQOOYsgvcPf'
        's6dg2NLgG/EIHvWy1apND/G8yI0FBGyYm6h9/24OlE3zFpVhCeiCcqSNS0ZXDKGK5B2wojRrp0dIrzSAS/ujgZYlGjIS2IohnoW1'
        'HMym5TP5AXnOqo+xlxo3c0wLst3z8u6cWyCI8T5wm/0ambFxKJHGlvqaI/YRUnCqZCWS7wFVXLy/+fDz1ecvi4ury6vP17/Hf6DO'
        'dyScTa2CsDbi227fqWdXU9v1upo6wlfoSadRYzCuKx3gXnS4Mz/VSX+8Mf31ZTO5k7m9Ct0UnL9tJkYayjvKb6ysvtwY5mOmjZIi'
        'DRFsDInYkEgTkju/aPbauwtT5Ld3vduydae07COX0Ke+YXrMtf+7d9ArbrsB4RFLe2WoDRb9RGIPkXBkf2Btr9taQ7SGx+PGYWLr'
        '6bgu0j5XXZ4PODU6DADq3wcaCcEARpCnAgW91kSC2HTM9ck7pBFVxkhR94muIld/18hJs6l/VQ82U+tkeNIU2cEBCCnvCnHVpTUs'
        'UhyocIWoYf1jwI63Fp5IbPk0BOkzS5M/K20KpOMWJc0MjTjrNIXJGE162t6oEN+FFxsOxoUV3NBbvJKWShaNqHEfyQFvrgL5yGx2'
        '+z9TVNZpxR6zMxPJZN1bArZDqQ39QGS7XvcXr0nCQ8zzUoINsKpGNGhuqVMYfvVd8vYtZW4cbRHvdhe+6XdweshD67pTobHDYubS'
        'fWRvKxt93UED6nI0fqomP3drcgTAJ07rCKRcbFM4PN3J5wLvFBrkrksPXhIN8QnfYHOimKmUsF8by1wVo+FvaAFMlusdzT8Mx++O'
        'OH+wezesb8QkoSK1XGf1txu6P5m+yZ+e6P0WOXg91dvbvYKCbW/3cOb2DnOzEQk/SUQJaWXNcDb6uNydMVOJk4zjdHvLupv0FDFl'
        '8BPVWSSpSoDjF5xlfM9KYIc2JITNzGy7FYk2w1eNVj9jdbm0YcHOZ+T/eocPVg==',
    'templates/dashboard.html':
        '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',
    'templates/expense_form.html':
        'eNqVVM2O2jAQvvMUI0soIBWy7TlY2m73VrWVlltVrUw8EAvHSROHFqFc+lZ9nT5JJ7bDzwIrNgf/znzzfZPx7IaAvy0aWQNbiBqn'
        'mc01g2E72A1hoYt0DVZZjXSy20H0KJWNQC3JqURTI6CmIbqXMoK23Z9O4DGs5pVI11gRGMXweIR9AE8LQ9GtO0yk2kCqRV3PWCkM'
        'algWVT5xS8YHQF+SfeA9jz7aZT6H27ZNYnIbeIAOEnK0WSFn7NvXpzkLN+5Wi4UPO2NONuPzbkpid8EPhsqUjQW7LZEsKYMMlOx9'
        'wIgc95sKfzaqQrn3DV+pRYpZoSVSMJyupvC5MWn2Dj42NeWcsmbZS5+N0A0hUwaCuu+RixL9OM9BJ/yaNpEXjbGM37sZRv/+/B2/'
        'rtE0+QIrrzJ4B5n9rrZYztjd9O49g1yZfnlN/gUpHumtWlJhcVVUW8YfwupcSY0aU+vI780D/cO+Z8pPqFKlUhhIQRkItgrrrl5f'
        'CIKkKK0qzJGytKN9ZhdQj0QKIw9Z6AlRHmYzghi2nj1K/4jIb9jyy6g+5Dmz2FM7U0ZwnbgjMUnso11JdmD5LIkk459ofL1snJ3L'
        '+4lnyP3p2Rsq5djxQr3YQortKyVjio79Fxph5DMj9PjWN+6cgwC3voFvZ3fK8+SXh+srtb5orKWy8jzqZpErerldE3wSG4Q0E2aF'
        '9S1N0AOFRhp3jbBvimXfdrUy60lV/GI8EZBVuHQ6mko/k/koylRtu9IcO44PwqSok1jwJC75IImpf3PX2497/X9fgOv3',
    'templates/history.html':
        'eNqVVs2O2zYQvvspCBaGbGDXAtJLk8gqFttteiiyReJLUSwMWhxbwlKUII7SGI4vfau+Tp+kwx/Zli13t7qYHM5883H+6N2YwVcE'
        'LQ3jK2FglmOpOBvvR7sxW6kqe2ZYoAKS/FIYrJotu2UPX2vQBtiiEdkzNKRJAF6ZDI+WWaUJGp0wyd+knV3ukZKYZHSyrpqSlYB5'
        'Jef8w8OCs0wJY+Z8XSiExvB0xOhLZPHFr9xOiRUoRrZzblA0yNOfm6pMYic/0St03SLDbQ1zLgUCZ4XsTJgWJRw2X4RqabfbMSdg'
        '+33nOT64vk6CQsDTRfVaAlY9uHfLo3Pa/k/XGaFuKKA8vQ+rSxYGFGToXB/Ug/+j+UHdmVQ1FpXumPH0Tqkk9sK+JiWceLCMFZoF'
        'sAKMTTs7+84w6baZvatFKNbMcwS57Bix+ZwUxvvuwFcaaY73abC9yogULakTEknscS4ju2oRiZXPkWlXZYGHIlyhvi20KjRQBOpa'
        'bVkoyyT2ZgFDsLyBtbtT26gl+Z5EodCjqbvkCSDBPVO2FIgmiUU6SmLbBLYZ6n7xg7zFCoWypUU/zOTVn/odpRObSm/Sf/76m/zx'
        '8ezNmn+zEAInneHSGU5djIJ6Etep608K4aap2hpkF6CQQym2N6xAKI1NZtCZOcFk2unaSuxo1kKDOqmcJP/+LBU7C0os+sVlyLDD'
        'oPPulkMXct6/mbacCMSmoKjDPBJl1WqMpuF+hHbCIT4lkaBYKTirbcxByPSyPrFJ6Sxd2JmXxLSyu2NXBcHHCg+n3SV0W1KBOFYH'
        'Pb+ICbTvPR5wn+CqkttLSiExYPPhEzPUV+cujgfSdgr8EbkxHj25cKG8rt3PTEWNYHCrqC9WNOxtQWj5zib1/m7x8OHx0+/L+8df'
        'Hz99nm0AJ+Sma93o6YZF3/0g374V4Or/PU9Dnjyfo+KLlLyBpqCTMsUiil4y6SVlqKYIL1TQ0/S1YCKzg8bwYcWrQwBkgUvwT190'
        'w8JqSZOYSBTSE+DpA6m5WXAVvPdO/vb4ecGv6vrPE+6zkTQCEV7m8wI0xcGNyTlvANtG27d+XTTlJPrJOWBIs6/D/jGavv+PqL1q'
        'BEuhN9Dw1MP3Z+8gYJiow2dD2b7s06svSVDvNywJjoPm5HXpIdiNMvCqSXp4CqCskV7nj1UXUMOohrN8NlxwQspDfn1t3UnJqKmD'
        '0FbZzD0FJ0xPntbR6Owf3b9RU+CH',
    'templates/logged_out.html':
        'eNp1U7Fu2zAQ3f0VVwKGW8CymkwZJHVIkyxFm8EdMgUUeZaI0KRAnuwYhv69FGUFruzcIvHuUe/du1P25eef+/XL8wPUtNXFLOsf'
        'oLmpcoaGFbOQQS6LGYTItkgcRM2dR8rZ3/VjcsfOS4ZvMWc7hfvGOmIgrCE0AbpXkupc4k4JTOJhCcooUlwnXnCN+c3qe88Wv0WK'
        'NBa/bFWhBNsSJPDw3qDxCGvHxRu6LB0wpwtamTdwqHPm6aDR14jEYmmI2uEmZ8cjtE6/bqz7uvDESYnFEjZKY5S9iFdXwvvFN+i6'
        'ICZLh9ZnWWnlYeSSagdCc+9z1rfHlUE3Kr8AcCfPa7Fe3xTP6Lw1XF+2FYpT+G3xYluo+Q6hRDSgP3wJ8NspvBm5fVtGj04DOo/j'
        'HNQmDgvm3ZO1sjzgEoI9MdV1qx6BRgbQvAvkDjx6r6wJKnxfQLn6nzVtpjr4FdODcmVGd6eisrIlChR0aMIODQfWL4EywKtgc5YO'
        'yWJCzT+1oLQBv00I3+kK4W/cQ40Of1xKuSbeYaU8oTvpv3fICYEHcULY1lAU8rkpWRr2Ytyh03voaFisMMj49/0DjZv+Wg==',
    'templates/login.html':
        'eNqtVU1v2kAQvfMrppYiEimEJqceMD006alqUEsOPUWLPeBV1rvu7hiCEP+947VN8FeqSt2LwW/efDzPzM4+3D9+Wf5aPEBCqZqP'
        'ZsUDlNCbMEAdzEf8BkXMT+AzS5EERImwDikMnpZfJ5+CBqZFimGwlbjLjKXAI+WJjCbUzNrJmJIwxq2McOL/XIPUkqRQExcJheHt'
        'zceTV5KkcP7NbKSGCTy8ZqgdwtKK6AXtbFrCla2S+gUsqjBwtFfoEsRGConFdRgcDpBb9bw29nLsSJCMxtewlgp97mNPvYmcG1/B'
        '8egVmFYSjGYrE+/raLHcQqSEc2FQ1CakRlun3TEQNj7HPJ7czhdondFCdQtjsG1+V8rA2F0by+pALl95STgYtE6pIRlIhRYbhL3J'
        'LWAZ1zXdTbOi2vNXhwvYSUogReeY7CCEDdLzmqMmGD/Xry+v4OI46oRmtly/cftMKjP+KrUdN8XfKW2hK0JP+Y1Ah1OQ43HY75Qd'
        'zwdTRR0X2Q7UyyiX3AZLwCtZQE3V2VvKeVFi4jBYPP5cBiAikkY3e1YV3/HUnJ2klVihKnQMg6KhB5T4zlCXO/XkPq9SZzn1eqJ9'
        'xhNP+NoYtbcj4yqRXrTcF8N4pkSEiVExcj0PvEFs2bfDDIu/c2kx7oDtlm6rlXED7Yyf0z6/iwr+n6qdQg4q975Fqd77NkMKvs/6'
        'NxVXOZHRVVG8glJJAyr6JdQjYemhvdamxUi0I74tu5VhUjrxvdcj/73RY4JEbBGE5lGKTK7pc0/6oudmsLiRjsWqB62vmB+VTU89'
        'olNKdn41nG2W+jdrUF4uvN/9VfwH9qzQzg==',
    'templates/register.html':
        'eNq1Vslu2zAQvfsrWAKBEyCOm5x6kFQEaXoqGqN1Dz0ZNDm2iFCkSlJ2DMP/3tFmR5tbdOFBkjlvtsfhjIM3H54e5t9njyT2iYpG'
        'Qf4iiul1SEHTaIQ7wEQ0IriCBDwjPGbWgQ/pt/nHyTv6WqRZAiHdSNimxnpKuNEeNEK3Uvg4FLCRHCbFj2sitfSSqYnjTEF4e/M2'
        '91bY8tIriL7AWjoPlkzI40sK2gGZW8afwQbTElHBldTPxIIKqfM7BS4G8LQQlSu2sArpfk8yqxYrYy/HzjMv+fiarKSCIuhxoXrD'
        'nRtfkcMBQwmmZeKjYGnErvYl5IZwxZwLaZ4ckxpsHXcHwKx4LSvk8W00A+uMZqqbFgrb8LvowQLzQO45N5n2CLprg9Lao8uWBTPV'
        'obxeRza9IQnTbA1kZzKLp8BNAoRpQaAMxzWNT1N019jaX5Ct9DFJwDm040hI1uAXK4whBrGoty+vyMVh1AkEteXqpNsHqWB4VDUO'
        'w/y1Spv/SqGHjIaj/dHJ4TBsd4qGo8FQQYs82oF8UYopt4WloGAyFzVZR2sJxuVjI0I6e/o6p4RxL41uFrKtTrUu2o73QLElqJzK'
        'kOaFTqPP+AymxXYfXuo0871p+l2Kl9vDS+NynZYUlYteadkahuWpYhxiowRgpI86r9SiPoc1LPzIpAXREbbrtc1DitWxNfndnFVf'
        'f8HH0dggJ+cRJS/nMT3cnFf4Y2qwp62kTRYninrtP5QwUvPXtfk/Ce0EeYbY38M2CK6T+5cULzPvja4yxC6dSD9Abd2neygtjbSb'
        '/zRvFW2np5GwNKiUTIpr2/V4r3C4iB2J2SafAdhjiiHzvuud9YxRZdZS162nL5lPOaAnExb1zJi+Vlt/Y/LlEMbxV/xP+Qlr0CLO',
    'templates/reports.html':
        'eNqtWM1u4zYQvucpBly4zgK17Dg/QLOygO6ihx7aAt29LQKDEmlJiCQaFO3EyObSt+rr9Ek6JCWbkujE2zQIYlMazu8335B5GgF/'
        'VLxiNZCY1jzIVFkQGD2fPY0gLkRyDypXBccnf/K1kKqGCfzyuOZVzeGLpMk9lyiJCqwwbjzsTESFqpV5GGbz6FNGtYIfQFpV4RQf'
        'Gvl8BZVQkNF6yaiidgfLt5AUtK4XZE0rXpDoDPAnXLdPeblWOxL9LsBs2nEVQEghk3y1IE9PsJHFciXk+ZgytuTW6fF7eH4m0c+M'
        'Aa2geRhOaQRKQM05JMbJIJyuo7Nwij5YD3lR8zY69DavElHy5abmbLnmMtFh5rUJohKVkTzqf3YZ/Wq2g96OqgB9LTFX2bKgMS/Q'
        'QczMZSPtaEmommScskaReV2j6uifv/5GFWQUzFfkG0ZcUnVuFdYYn9Ihg/kGYgU+YRuOkbNfw6lR7NhRUlRpZHde9Hd2EqHVjFCB'
        '3WGjsInsBxRT6cbSfTNZ5QVCsVa7gi/IQ85Udqsz9dVj8ke4mM3uvpWYS7T9AWIEZirFpmK38G5+c3VzffmBRK4X9mvzYRGMZe3j'
        'zoBhkspc53zgvlvVtrKf11pTlUK8A6wXT4XcwflIJ14JRYv3h9LavG7TVh0T1UYR2Ob84aN4XJAZzOBqjr8EpNA5yMuUAJU5nRic'
        'LIjPmOOPMZDkMsH+TVDh/IJAsrOfckEuroOfLq6vCehEL4jGrU63FPdo6x1P+Gp10T6YmPwvyI3OolXZtYMpRESAgbMJROfyDY50'
        '9rY/rXOIAhYkokCD2MwDF1/YO2G0xppKumu06LWGvVmkdK0VvrZfrFY1V40CuzCkMtgXGu6MrLstGJ6fb709yAILEO3N+aDPWOB2'
        'F6LIqu6m+FhlECW6OL2KvFqyRgj7ggUY9UNDTx6pUOEUgccmJerRlKVNsdqZpRaZ0CrJBJa8zBkrEG4u9C2qScMxs2OxY+ioKfJ5'
        'um/ik+LfO61hqNE4C+anuGnK1Dr7RS98Lg20X52smxwI3clCKmnFlnuM9G0i4W5TZ7kpWs0FTzEB5Hv7tcgjM10ODqo9G7v82mlG'
        'w7JmdPRBfwqm0eTrpQunm6JD4ifx8m96HBY7MwY1ZfZo2NltBufEML8/Z6XOmZGqB0kb6hGFjxjcxFrB7bG6l4FT8+5UPm6WSk49'
        'dv3Cegy3lc14nmbKVLUM7MKM1M707JKO//EwwkN7l8HhoDOMyKPxCBD643x/YHvp7PWpxWSMObpn4qHqOsvorm1D09xesh40ownD'
        'ObYpGrtEHCp9cOszhIzw+d4h7OhMP2gdqTYlHlRL7DLlffUZIcr1weKAaS01RbVOjnqGQxULtvPiOta4PiRlwJbSN+DYySQR+0ki'
        'dkkC3WVeK53AfQWJ3S45RcmAjeL+lOmXa9rPwBFUOhnGhcWBc5PACRVvWMrVEvuufu2m8NGIwra2B/jbl+4KnTp2TfiuElI8HDl9'
        'ey4ah8vGW+rtXCN6dW9eePnANahdw/rVx1BwuPBMwS9R5GWufGza453jF5XvuKzsQTW8lwxT1DXfXTbACWqFWYPFAsZiy+W4g7xe'
        'BetNDEZ8okVJ9Af+bXAxVN45OjmvOxh/7brUB287dO19/7+xo9Hh5b/26PUWzpP7WV7sltgQ9cm0h+WTX8dm6/juTdSFagx3je/8'
        '7PV/Ec+hZr3/2PwLEVw7aA==',
}

here = os.path.dirname(os.path.abspath(__file__))
target = os.path.join(here, "expense_tracker")

if os.path.exists(target):
    n = 2
    while os.path.exists(os.path.join(here, f"expense_tracker_{n}")):
        n += 1
    target = os.path.join(here, f"expense_tracker_{n}")
    print("A folder named expense_tracker already exists, so a new one is used.")

for name, data in FILES.items():
    path = os.path.join(target, *name.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(zlib.decompress(base64.b64decode("".join(data) if not isinstance(data, str) else data)))
    print("created", name)

print()
print("Done. Project folder:", target)
print("Next: open that folder in VS Code (File > Open Folder), then run:")
print("    python check.py")
print("    python app.py")
