# PDF Ebook Text Extraction & Cleaning Tool wtih RESTful Server

## Structure of This Document

* [Introduction](#intro)
* [Getting Started](#system-setup)
* [Admin Site](#admin-site)
* [RESTful API](#api) 


## <a name="intro" style="color: #000;"> Introduction </a>

### Background

PDF ebooks usually have table of content (TOC). Hence, the texts in a PDF ebook are naturally in a certain hierarchy. Such text and hierarchy information extracted from PDF ebooks can be used for research in machine learning (especially hierarchical text classification) and natural language processing.

The goal of this project is to provide a tool to manage and maintain a huge database of texts extracted from PDF ebooks and allow users to access and upload data through RESTful API endpoints. This project enable easy sharing and hence facilitates collaboration among researchers in a team, or across different teams.

### Project Scope

The purpose of this project is to provide a RESTful backend and an admin site to 

* Organize and manage PDF ebooks
* Extract TOC hierarchy and section texts from PDF ebooks
* Store all data extracted from PDF ebooks in relational databases
* Access the TOC, text and more through a handlful of RESTful APIs
* Post your own version of processed texts of a book/chapter and share with other researchers
* (*Optional) clean up and lemmatize the extracted texts using the built-in cleaner.

### Skills & Tools Required

* **[Adobe Acrobat](https://acrobat.adobe.com/us/en/acrobat.html) (2015 DC or later) is required** to pre-process the PDF files and convert them into HTML files split by bookmarks. The PDF and HTML files will be then fed into the system.
* **Adequate knowledge of [Django](https://www.djangoproject.com/) is required** to be able to maintain and further expand this project. Please make sure you understand Django well enough before reading the rest of this document.
* Due to copyright issues, we cannot distribute PDF ebooks or any processed text extracted from them. This project contents only the source code, without any database or files. You are supposed to setup your own database and connent to it before running the system.

### Text Cleaning Techniques

The built-in cleaner can perform the following operations sequentially on the extracted texts:

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

However, the cleaner is **NOT enabled by default**. You may manually enable the cleaner or customize the cleaning procedure by modifying the source code in the `extractor` package.


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

### Object-level Authentication and User Groups

The server manages authentication at the object level - each Book/ Section/ Version/ Content object is only visible to certain users, among those only certain users are able to edit the object. Authentication is done through extending two classes `OwnerAndSuperuserOnlyAdmin` and `SuperuserOnlyAdmin` in the module `pdf_server.admin`.

To facilitate authentication, users are split into two groups: Superusers (can do anything), and Normal users (can only create, cannot edit certain objects unless is object creator).

More information on the authentication and user groups can be found in the source code, as well as the [API](#api) documentation below.

### Create an Entry for the `Book` Model

The following fields are required to create a new entry.

| Field | Explanation  
| --- | --- 
| Title | The title of the PDF book 
| Toc html path | The full path of the html file generated by Adobe Acrobat that contains the table of content*.

**\*NOTE**: There must be a directory of the same name next to the html fie. This is the default output format of Adobe Acrobat when converting PDF to HTML with the "Split by Bookmarks" option turned on. e.g.

### Process a Book

After creating a `Book` entry,

1. Go back to the model page `/admin/book/book`
1. Tick the book that was newly created
1. Select "Process book" in the "Action" dropdown menu
1. Click "GO"

This will take from a few seconds to a few minutes for most cases, depending on the structure and the length of the book. It will take a lot longer to process a book if you enable the text cleaner. 

Most importantly, <mark>DO NOT close the browser tab or shut down the server while a book is being processed</mark>. Data integrity could NOT be preserved (in other words, the system WILL fail) if the process is interrupted in the middle.

You can view the progress in the terminal where you started the Django server.


## <a name="api" style="color: #000;"></a> RESTful API

### Overview

The docs and an emulated client are available at `http://<your-domain>/docs/`

The root URL of all RESTful APIs is `/api/v1` (e.g. the book-list api is at `http://<your-admin>/api/v1/book/list/`). There are four sub-groups of API endpoints: `Book`, `Section`, `Version` and `Content`. Only authenticated users can access any of the APIs listed below (authentication is done using Django's basic authentication service).

| Group | URL |
| --- | --- | 
| [Book](#api-book) | `/book` 
| [Section](#api-section) | `/section`
| [Version](#api-version) | `/version`
| [Content](#api-content) | `/content`

### <a name="api-book" style="color: #000;"></a> Book

| Endpoint | URL | Method | Permission |
| --- | --- | --- | --- |
| [List](#book-list) | `/list/` | GET | Any user |
| [Detail](#book-detail) | `/detail/{pk}/` | GET | Any user |
| [TOC](#book-toc) | `/toc/{pk}/` | GET | Any user |

#### <a name="book-list" style="color: #000;"></a> List

HTTP responses:

| Case | HTTP Response |
| --- | --- |
| Successful | `200 OK` |
| Login credentials not accepted | `401 Unauthorized` | 

Example of response data if successful:

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

HTTP responses:

| Case | HTTP Response |
| --- | --- |
| Successful | `200 OK` |
| Login credentials not accepted | `401 Unauthorized` | 
| No such book available | `404 Not Found` |

Example of response data if successful:

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

HTTP responses:

| Case | HTTP Response |
| --- | --- |
| Successful | `200 OK` |
| Login credentials not accepted | `401 Unauthorized` |
| No such book available | `404 Not Found` |

Example of response data if successful:

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

| Endpoint | URL | Method | Permission |
| --- | --- | --- | --- |
| [Detail](#section-detail) | `/detail/{pk}/` | GET | Any user |
| [Children](#section-children) | `/children/{pk}/` | GET | Any user |
| [Versions](#section-versions) | `/versions/{pk}/` | GET | Any user |
| [Partial TOC from section](#section-toc) | `/toc/{pk}` | GET | Any user |

#### <a name="section-detail" style="color: #000;"></a> Detail

Parameters in URL:

| Parameter | Type | Explanation |
| --- | --- | --- |
| `pk` | `int` | The id of the section |

HTTP responses:

| Case | HTTP Response |
| --- | --- |
| Successful | `200 OK` |
| Login credentials not accepted | `401 Unauthorized` |
| No such section available | `404 Not Found` |

Example of response data if successful:

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

HTTP responses:

| Case | HTTP Response |
| --- | --- |
| Successful | `200 OK` |
| Login credentials not accepted | `401 Unauthorized` |
| No such section available | `404 Not Found` |

The response is an array of "Detail"s in the `/detail/{pk}/` API denoting the children of the queried section.

#### <a name="section-versions" style="color: #000;"></a> Versions

Parameters in URL:

| Parameter | Type | Explanation | 
| --- | --- | --- |
| `pk` | `int` | The id of the section |

HTTP responses:

| Case | HTTP Response |
| --- | --- |
| Successful | `200 OK` |
| Login credentials not accepted | `401 Unauthorized` |
| No such section available | `404 Not Found` |

Example of response data if successful:

```json
[
	{
		"id": 1,
		"name": "Raw",
		"created_by": null,
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

The response is an array of all the versions associated with the section. See the [Version](#api-version) API below for more details.

#### <a name="section-toc" style="color: #000;"></a> Partial TOC from section

Parameters in URL:

| Parameter | Type | Explanation | 
| --- | --- | --- |
| `pk` | `int` | The id of the section |

HTTP responses:

| Case | HTTP Response |
| --- | --- |
| Successful | `200 OK` |
| Login credentials not accepted | `401 Unauthorized` |
| No such section available | `404 Not Found` |

Example of response data if successful:

```json
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
}
```

The response is the partial TOC starting from the queried section. For more details on TOC, see the [TOC](#book-toc) API (under Book) above.

### <a name="api-version" style="color: #000;"></a> Version

| Endpoint | URL | Method | Permission |
| --- | --- | --- | --- |
| [List](#version-list) | `/list` | GET | Any user |
| [Detail](#version-detail) | `/detail/{pk}/` | GET | Any user |
| [Create](#version-create) | `/create/` | PUT | Any user |
| [Update](#version-update) | `/update/{pk}/` | POST | Version creator |
| [Delete](#version-delete) | `/delete/{pk}/` | DELETE | Version creator |

#### <a name="version-list" style="color: #000;"></a> List

HTTP responses:

| Case | HTTP Response |
| --- | --- |
| Successful | `200 OK` |
| Login credentials not accepted | `401 Unauthorized` |

Example of response data if successful:

```json
[
	{
		"id": 1,
		"name": "Raw",
		"created_by": null,
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

The response is an array of "Version"s. The default version, "Raw" is included.

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

HTTP responses:

| Case | HTTP Response |
| --- | --- |
| Successful | `200 OK` |
| Login credentials not accepted | `401 Unauthorized` |
| No such version available | `404 Not Found` | 

Response data if successful:

```json
{
	"id": 1,
	"name": "Raw",
	"created_by": null,
	"timestamp": "2016-09-02 20:00:00"
}
```

The response is a single element of the array returned by the [List](#version-list) API above.

#### <a name="version-create" style="color: #000;"></a> Create

Request example:

```json
{
	"name": "Cleaned text for coref"
}
```

HTTP responses:

| Case | HTTP Response |
| --- | --- |
| Successful | `201 Created` |
| Login credentials not accepted | `401 Unauthorized` | 

Example of response data if successful:

```json
{
	"id": 3,
	"name": "Cleaned text for coref",
	"created_by": "admin",
	"timestamp": "2016-09-02 22:00:00"
}
```

#### <a name="version-update" style="color: #000;"></a> Update

Parameters in URL:

| Parameter | Type | Explanation 
| --- | --- | --- |
| `pk` | `int` | The id of the version

Request example:

```json
{
	"name": "Diff name"
}
```

HTTP responses:

| Case | HTTP Response |
| --- | --- |
| Successful | `200 OK` |
| Login credentials not accepted | `401 Unauthorized` | 
| User is not the version creator | `403 Forbidden` |
| No such version available | `404 Not Found` |

Example of response data if successful:

```json
{
	"id": 3,
	"name": "Diff name",
	"created_by": "admin",
	"timestamp": "2016-09-02 22:00:00"
}
```

#### <a name="version-delete" style="color: #000;"></a> Delete

Parameters in URL:

| Parameter | Type | Explanation 
| --- | --- | --- |
| `pk` | `int` | The id of the version

HTTP responses:

| Case | HTTP Response |
| --- | --- |
| Successful | `204 No Content` |
| Login credentials not accepted | `401 Unauthorized` | 
| User is not the version creator | `403 Forbidden` |
| No such version available | `404 Not Found` |

When a version is deleted, all contents associated with that version will be deleted as well. For more details on contents, see the [Content](#api-content) API below.

### <a name="api-content" style="color: #000;"></a> Content

| Endpoint | URL | Method | Permission |
| --- | --- | --- | --- |
| [Immediate Text](#content-immediate) | `/immediate/{section}/{version}/` | GET | Any user | 
| [Aggregate Text](#content-aggregate) | `/aggregate/{section}/{version}/` | GET | Any user |
| [Post](#content-post) | `/post/{section}/{version}/` | POST | Version creator |

#### <a name="content-immediate" style="color: #000;"></a> Immediate Text

Parameters in URL:

| Parameter | Type | Explanation 
| --- | --- | --- |
| `section` | `int` | The id of the section
| (*optional) `version` | `int` | The id of the version. <br> If no version is specified, the raw version will be chosen by default.

HTTP responses:

| Case | HTTP Response |
| --- | --- |
| Successful | `200 OK` |
| Login credentials not accepted | `401 Unauthorized` |
| No such section/ version available | `404 Not Found` |

Example of response data if successful:

```
The response body contains the clear text of a certain version of the section. 
```

#### <a name="content-aggregate" style="color: #000;"></a> Aggregate Text

Parameters in URL:

| Parameter | Type | Explanation 
| --- | --- | --- |
| `section` | `int` | The id of the section
| (*optional) `version` | `int` | The id of the version. <br> If no version is specified, the raw version will be chosen by default.

HTTP responses:

| Case | HTTP Response |
| --- | --- |
| Successful | `200 OK` |
| Login credentials not accepted | `401 Unauthorized` |
| No such section/ version available | `404 Not Found` |

Example of response data if successful:

```
The response body contains the clear text of a certain version of the section, 
and ALL ITS DESCENDANTS, in the original page order.
```

#### <a name="content-post" style="color: #000;"></a> Post

Parameters in URL:

| Parameter | Type | Explanation 
| --- | --- | --- |
| `section` | `int` | The id of the section
| `version` | `int` | The id of the version

The body of the request contains the location of the text file with contents of a specific version of a section, i.e. `output.txt`

HTTP responses:

| Case | HTTP Response |
| --- | --- |
| Successful | `200 OK` |
| Login credentials not accepted | `401 Unauthorized` | 
| User is not the version creator | `403 Forbidden` |
| No such section/ version available | `404 Not Found` |

