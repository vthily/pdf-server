# PDF Ebook Text Extraction & Cleaning Tool wtih RESTful Server

## Structure of This Document

* [Introduction](#intro)
* [Getting Started](#system-setup)
* [Admin Site](#admin-site)
* [RESTful API](#api) 
* [How to Contribute](#further-dev)

## <a name="intro" style="color: #000;"> Introduction </a>

### Context

PDF ebooks usually have table of content (TOC). Hence, the texts in a PDF ebook are naturally in a certain hierarchy. Such text and hierarchy information extracted from PDF ebooks can be used for research in machine learning (especially hierarchical text classification) and natural language processing.

### Project Scope

The purpose of this project is to provide a RESTful backend and an admin site to 

* Organize and process PDF files
* Extract table of content (TOC) tree and store it in a relational database
* Extract cleaned and lemmatized plain text
* Maintain the hierarchical structure of the extracted texts according to the (TOC)
* Generate WordCloud images for all chapters, sections, and sub-sections
* Access the TOC, plain text content (by chapter or section), WordCloud images and more through RESTful APIs

### Skills & Tools Required

* **[Adobe Acrobat](https://acrobat.adobe.com/us/en/acrobat.html) (2015 DC or later) is required** to pre-process the PDF files and convert them into HTML files split by bookmarks. The PDF and HTML files will be then fed into the system.
* **Adequate knowledge of [Django](https://www.djangoproject.com/) is required** to be able to maintain and further expand this project. Please make sure you understand Django well enough before reading the rest of this document.
* Due to copyright issues, we cannot distribute PDF ebooks or any processed text extracted from them. This project contents only the source code, without any database or files. You are supposed to setup your own database and connent to it before running the system.

### Text Cleaning Techniques

The built-in cleaner performs the following operations sequentially on the extracted texts:

1. Perform known replacements (e.g. "ﬁ" --> "fi"; if you don't see any difference, try to copy the first "ﬁ" as TWO letters, "f" and "i". You will realize you can't, because "ﬁ" is actually ONE unicode character)
1. Replace non-ascii characters with underscore ("_")
1. Remove all URIs
1. Remove all emails
1. Remove stop words according the the MySQL stop word list
1. Remove all punctuation marks
1. Remove all digits
1. Remove one-letter and two-letter words
1. Remove redundant whitespace characters
1. Lemmatize

You may customize the text cleaning procedure by adding/removing individual steps in the `Cleaner` class in `crawler/cleaner.py`. See more in [How to Contribute](#future-dev).


## <a name="system-setup" style="color: #000;"></a> Getting Started

1. Install [Python 3](https://www.python.org/downloads/)
1. Clone the project
1. Install python dependencies: </br> `$ pip install -r requirements.txt`
1. Download [WordNet data for NLTK](http://www.nltk.org/data.html)
1. Setup your own database and update the connection configuration in `settings.py`, then migrate.
1. Run the development server <br> `$ python3 manage.py runserver`

The following additional steps are **for Ubuntu users ONLY**:

1. Install package `libjpeg-dev` </br> `$ sudo apt-get install libjpeg-dev`
1. Install package `libfreetype6-dev` </br> `$ sudo apt-get install libfreetype6-dev`
1. Reinstall `pillow` </br> `$ pip uninstall pillow`</br> `$ pip install pillow`

## <a name="admin-site" style="color: #000;"></a> Admin Site

This is a standard admin site of Django. It can be accessed by the URL `<your-domain>/admin/`. If you are running the default Django development server, the complete URL is [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).

You may need to create a superuser for the first time to log in to the admin site. This can be done by

```bash
$ python3 manage.py createsuperuser
```

If you didn't know about this yet, please learn Django first before trying the following steps. See [Introduction](#intro).

### Create an Entry for the `Book` Model

The following fields are required to create a new entry.

| Field | Explanation | Required for New Entry | 
| --- | --- | --- | 
| Title | The title of the PDF book | YES
| Toc html path | The path of the html file generated by Adobe Acrobat. There must be a directory of the same name next to the html file. This is the default output format of Adobe Acrobat when converting PDF to HTML with the "Split by Bookmarks" option turned on. | YES
| Target dir path | The path of the directory where the extracted, cleaned and structured plain text files will be stored. By default it's the `target` directory.| Optional |

**Please leave all other fields unmodified.**

### Process a Book

After creating a `Book` entry,

1. Go back to the model page `/admin/book/book`
1. Tick the book that was newly created
1. Select "Process book" in the "Action" dropdown menu
1. Click "GO"

This will take from a few seconds to 10+ minutes for most cases, depending on the structure and the length of the book. Most importantly, <mark>DO NOT close the browser tab or shut down the server while a book is being processed</mark>. Data integrity could NOT be preserved (in other words, the system WILL fail) if the process is interrupted in the middle.

You can view the progress of the process in the terminal where you started the Django server.

## <a name="api" style="color: #000;"></a> RESTful API

### Overview

The docs and an emulated client are available at `http://<your-domain>/docs/`

The root URL of all RESTful APIs is `/api/v1` (e.g. the book-list api is at `http://<your-admin>/api/v1/book/list/`). There are four sub-groups of API endpoints: `Book`, `Section`, `Version` and `Content`.

| Group | URL |
| --- | --- | 
| [Book](#api-book) | `/book` 
| [Section](#api-section) | `/section`
| [Version](#api-version) | `/version`
| [Content](#api-content) | `/content`

### <a name="api-book" style="color: #000;"></a> Book

| Endpoint | URL | Method | 
| --- | --- | --- | 
| [List](#book-list) | `/list/` | GET |
| [Detail](#book-detail) | `/detail/{pk}/` | GET |
| [TOC](#book-toc) | `/toc/{pk}/` | GET |

#### <a name="book-list" style="color: #000;"></a> List

Response example:

```json
[
	{
		"id": 2,
		"title": "My Sample Handbook",
		"root_section": 25
	},
	{
		"id": 3,
		"title": "My Sample Textbook",
		"root_section": 72
	}
]
```

More details on the fields:

| Field | Type | Explanation | 
| --- | --- | --- | 
| `id` | `int` | The id of the book |
| `title` | `string` | The title of the book |
| `root_section` | `int` | The id of the root section that represents the entire book |

#### <a name="book-detail" style="color: #000;"></a> Detail

Parameters in URL:

| Parameter | Type | Explanation |
| --- | --- | --- |
| `pk` | `int` | The id of the book |

Response example:

```json
{
	"id": 7,
	"title": "Digital Signal Processing System Analysis and Design",
	"root_section": 1011
}
```

This is a single element of the list returned by the [List](#book-list) API above.

#### <a name="book-toc" style="color: #000;"></a> TOC

Parameters in URL:

| Parameter | Type | Explanation |
| --- | --- | --- |
| `pk` | `int` | The id of the book |

Response example:

```json
{
	"title": "My Sample Handbook",
	"id": 25,
	"children": [
		{
			"title": "Chapter 1",
			"id": 26,
			"children": [
				{
					"title": "Section 1.1",
					"id": 27,
					"children": []
				},
				{
					"title": "Section 1.2",
					"id": 28,
					"children": []
				}
			]
		},
		{
			"title": "Chapter 2",
			"id": 29,
			"children": []
		}
	]
}
```

This is a nested, recursive JSON that represents the table of content tree. Each node in the tree has the following fields:

| Field | Type | Explanation | 
| --- | --- | --- | 
| `title` | `string` | The title of the section |
| `id` | `int` | The id of the section |
| `children` | `array` | An array of immediate children nodes of the current node | 

### <a name="api-section" style="color: #000;"></a> Section

| Endpoint | URL | Method |
| --- | --- | --- |
| [Detail](#section-detail) | `/detail/{pk}/` | GET |
| [Children](#section-children) | `/children/{pk}/` | GET |
| [Word Cloud](#section-wordcloud) | `/wordcloud/{pk}/` | GET |

#### <a name="section-detail" style="color: #000;"></a> Detail

Parameters in URL:

| Parameter | Type | Explanation |
| --- | --- | --- |
| `pk` | `int` | The id of the section |

Response example:

```json
{
	"title": "Section 1.1",
	"id": 27,
	"has_children": false
}
```

#### <a name="section-children" style="color: #000;"></a> Children

Parameters in URL:

| Parameter | Type | Explanation |
| --- | --- | --- |
| `pk` | `int` | The id of the section |

The response is an array of "Detail"s in the `/detail/{pk}/` API.

#### <a name="section-wordcloud" style="color: #000;"></a> Word Cloud 

Parameters in URL:

| Parameter | Type | Explanation | 
| --- | --- | --- |
| `pk` | `int` | The id of the section |

The response has the HTTP header `Content-Type: image/jpeg` that is a word cloud image generated based on the aggregated text of the section itself and all its descendents in the TOC tree.

### <a name="api-version" style="color: #000;"></a> Version

| Endpoint | URL | Method | Permission | Auth
| --- | --- | --- | --- | --- |
| [List](#version-list) | `/list` | GET | None | None
| [Detail](#version-detail) | `/detail/{pk}/` | GET | None | None
| [Create](#version-create) | `/create/` | POST | Any user | Basic
| [Update](#version-update) | `/update/{pk}/` | POST | Version creator | Basic
| [Delete](#version-delete) | `/delete/{pk}/` | POST | Version creator | Basic

#### <a name="version-list" style="color: #000;"></a> List

Response example:

```json
[
	{
		"id": 1,
		"name": "Cleaned text for human readers",
		"created_by": "admin",
		"timestamp": "2016-09-02 20:00:00"
	}
	{
		"id": 2,
		"name": "Cleaned text for machine",
		"created_by": "admin",
		"timestamp": "2016-09-02 21:00:00"
	}
]
```

The response is an array of "Version"s.

More details on the fields:

| Field | Type | Explanation | 
| --- | --- | --- | 
| `id` | `int` | The id of the version
| `name` | `string` | The name of the version
| `created_by` | `string` | The user id for the creator of the version
| `timestamp` | `string` | The timestamp for version creation

#### <a name="version-detail" style="color: #000;"></a> Detail

Parameters in URL:

| Parameter | Type | Explanation 
| --- | --- | --- |
| `pk` | `int` | The id of the version

Response example:

```json
{
	"id": 1,
	"version_name": "Cleaned text for human readers",
	"created_by": "admin",
	"timestamp": "2016-09-02 20:00:00"
}
```

The response is a single element of the array returned by the [List](#version-list) API above.

#### <a name="version-create" style="color: #000;"></a> Create

The body of the request contains the name of a new version in JSON format, i.e. `name="Cleaned text for coref"`

Response example:

```json
{
	"id": 3,
	"version_name": "Cleaned text for coref",
	"created_by": "admin",
	"timestamp": "2016-09-02 22:00:00"
}
```

If a non-authenticated user access the API, the response should be `HTTP_401_UNAUTHORIZED`.

#### <a name="version-update" style="color: #000;"></a> Update

Parameters in URL:

| Parameter | Type | Explanation 
| --- | --- | --- |
| `pk` | `int` | The id of the version

The body of the request contains the updated attributes of a version in JSON format, i.e. `name="Diff name"`

Response example:

```json
{
	"id": 3,
	"version_name": "Diff name",
	"created_by": "admin",
	"timestamp": "2016-09-02 22:00:00"
}
```

If a non-authenticated user access the API, the response should be `HTTP_401_UNAUTHORIZED`.

If a user that is not the creator of the specific version access the API, the response should be `HTTP_403_FORBIDDEN`.

#### <a name="version-delete" style="color: #000;"></a> Delete

Parameters in URL:

| Parameter | Type | Explanation 
| --- | --- | --- |
| `pk` | `int` | The id of the version

Response example:

`HTTP_200_OK`

If a non-authenticated user access the API, the response should be `HTTP_401_UNAUTHORIZED`.

If a user that is not the creator of the specific version access the API, the response should be `HTTP_403_FORBIDDEN`.

### <a name="api-content" style="color: #000;"></a> Content

| Endpoint | URL | Method | Permission | Auth  
| --- | --- | --- | --- | --- |
| [Get Immediate](#content-immediate) | `/immediate/{section}/{version}/` | GET | None | None
| [Get Aggregate](#content-aggregate) | `/aggregate/{section}/{version}/` | GET | None | None
| [Post](#content-post) | `/post/{section}/{version}/` | POST | Version creator | Basic

#### <a name="content-immediate" style="color: #000;"></a> Get Immediate 

Parameters in URL:

| Parameter | Type | Explanation 
| --- | --- | --- |
| `section` | `int` | The id of the section
| `version` | `int` | The id of the version

Response example:

`"processed text content"`

The response is the text of a specific version of a section.

#### <a name="content-aggregate" style="color: #000;"></a> Get Aggregate

Parameters in URL:

| Parameter | Type | Explanation 
| --- | --- | --- |
| `section` | `int` | The id of the section
| `version` | `int` | The id of the version

Response example:

`"processed text content"`

The response is the aggregated text of a specific version of a section.

#### <a name="content-post" style="color: #000;"></a> Post

Parameters in URL:

| Parameter | Type | Explanation 
| --- | --- | --- |
| `section` | `int` | The id of the section
| `version` | `int` | The id of the version

The body of the request contains the location of the text file with contents of a specific version of a section, i.e. `output.txt`

Response example:

`HTTP_200_OK`

If a non-authenticated user access the API, the response should be `HTTP_401_UNAUTHORIZED`.

If a user that is not the creator of the specific version access the API, the response should be `HTTP_403_FORBIDDEN`.

## <a name="further-dev" style="color: #000;"></a> How to Contribute

To be continued.
