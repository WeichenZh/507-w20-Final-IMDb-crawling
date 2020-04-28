my code includes 3 main parts.£º
1. Scraping and crawling data from the internet and save them in cache file. 
2. Creating database based on scrapped data. 
3. Collecting information and data from database for presentation. These parts are marked in the ¡°main¡± function.

Warning: Part 1 is really time consuming even with the cache. Thus, I strongly suggest running the program with existed database. If you want to test part 1 and 2, please input a small number k in the terminal.

Interacting: the main interacting is on the flask app. User can see the top-ranked movie list, movie¡¯s detail, most popular director, director¡¯s detail and the distribution of movie release date.

The distribution of release date
        this page will show you the distribution of release year of these top-k movies.

Most popular director
        this page will show you a list of directors ordered by the number of their movies on the top-k-movie list. You can also click the director¡¯s name to get his/her other famous movies.

Demo link: https://youtu.be/Dl93c2hUiC0
