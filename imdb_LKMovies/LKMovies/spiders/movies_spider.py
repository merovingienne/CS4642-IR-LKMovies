import scrapy

class MoviesSpider(scrapy.Spider):
    name = "movies"
    page_limit = 5

    def start_requests(self):
        urls = [
            "https://www.imdb.com/search/title?country_of_origin=lk"
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):

        if 'https://www.imdb.com/search/title?country_of_origin=lk' in response.url:
            # movie list page
            next_selector_string = '//*[@id="main"]/div/div/div[1]/div[2]/a[2]'
            if ("&page=") not in response.url:
                next_selector_string = next_selector_string[:-3]

            next_link = response.xpath(next_selector_string)

            # stop at given page number
            if ("&page=" + str(self.page_limit)) not in response.url:
                for link in next_link:
                    url = response.urljoin(link.xpath('@href').extract_first())
                    yield scrapy.Request(url, callback=self.parse)

            # movie page links
            movie_links = response.xpath('//*[@id="main"]/div/div/div[3]/div/div[3]/h3/a')

            for movie_link in movie_links:
                movie_url = response.urljoin(movie_link.xpath('@href').extract_first())
                yield scrapy.Request(movie_url)


        else:
            # movie details page
            title = response.xpath('//*[@id="title-overview-widget"]/div[2]/div[2]/div/div/div[2]/h1/text()').extract_first().strip()

            year = response.xpath('//*[@id="titleYear"]/a/text()').extract_first()
            if (type(year) == type(None)): return

            rating = response.xpath('//*[@id="title-overview-widget"]/div[2]/div[2]/div/div[1]/div[1]/div[1]/strong/span').extract_first()
            if (type(rating) != type(None)): rating = rating.strip()

            director = response.xpath('//span[@itemprop="director"]/a/span/text()').extract_first()
            if (type(director) != type(None)): director = director.strip()

            # multiple genres possible
            genres_list = []
            for genre in response.xpath('//*[@id="titleStoryLine"]/div[3]/a'):
                temp_genre = genre.xpath('text()').extract_first().strip()
                if (len(temp_genre)):
                    genres_list.append(temp_genre)

            # multiple writers possible
            writers_list = []
            for i in response.css('div.credit_summary_item').xpath('span[@itemprop="creator"]'):
                temp_writer = i.xpath("./a/span/text()").extract_first().strip()
                if (len(temp_writer)):
                    writers_list.append(temp_writer)

            # duration, if available, in minutes
            duration_string = response.xpath('//time[@itemprop="duration"]/text()').extract_first()
            duration_component_hours = 0
            duration_component_minutes = 0
            duration_total_minutes = 0


            if (type(duration_string) != type(None)):
                duration_strings = duration_string.strip().split()
                if (("h") in duration_string): # eg: 1h 23min
                    duration_component_hours = int(duration_strings[0][:-1])
                    if (len(duration_strings)>1): # no minutes
                        duration_component_minutes = int(duration_strings[1][:-3])
                else:
                    duration_component_minutes = int(duration_strings[0][:-3])

                duration_total_minutes = (duration_component_hours * 60) + duration_component_minutes





            # print("\n\ntitle: " + (title if type(title)!= type(None) else "") + "\nyear: " + (year if type(year) != type(None) else "") + "\ngenres: " + ",".join(genres_list))

            # print("\n\n\ntotal: %d minutes, (%d hours, %d minutes)" % (duration_total_minutes, duration_component_hours, duration_component_minutes))

            yield {
                'title': title,
                'year': year,
                'duration_total_minutes': duration_total_minutes,
                'duration_component_hours': duration_component_hours,
                'duration_component_minutes': duration_component_minutes,
                'rating': rating,
                'director': director,
                'writers': writers_list,
                'genres': genres_list,
            }