function extractBooks() {
    var books = Array.from(document.getElementsByClassName('bookalike'));
    return books.map(function(book) {
        var data = {};
        
        // Extracting data directly
        data['isbn'] = book.querySelector('td.field.isbn div.value').textContent.trim();
        data['isbn13'] = book.querySelector('td.field.isbn13 div.value').textContent.trim();
        data['title'] = book.querySelector('td.field.title').textContent.replace(/^title\s+|\s\s+/g, ' ').trim();
        var author_info = book.querySelector('td.field.author div.value a');
        data['author_name'] = author_info.textContent.trim();
        data['author_link'] = 'https://www.goodreads.com'  + author_info.getAttribute('href');
        data['avg_rating'] = parseFloat(book.querySelector('td.field.avg_rating div.value').textContent.trim());
        data['user_rating'] = book.querySelector('td.field.rating').textContent.trim();  // You need to convert this according to your STARS_ENUM in Python
        data['num_pages'] = parseInt(book.querySelector('td.field.num_pages div.value').textContent.trim());
        data['publishing_date'] = book.querySelector('td.field.date_pub div.value').textContent.trim();
        data['started_date'] = book.querySelector('td.field.date_started div.value').textContent.trim();
        data['finished_date'] = book.querySelector('td.field.date_read div.value').textContent.trim();
        data['added_date'] = book.querySelector('td.field.date_added div.value').textContent.trim();

        // Extract author id from the author link
        data['author_id'] = null;  // Initialize to null to handle cases where the regex might not find a match
        var author_id_match = /\/author\/show\/(\d+)./.exec(data['author_link']);
        if (author_id_match) {
            data['author_id'] = parseInt(author_id_match[1]);
        }

        
    return data;
});
}
return extractBooks();