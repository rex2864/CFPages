## libxml tutorial

(이전에 작성했었던 내용을 백업용으로 다시 올려둔다.)

Libxml tutorial 원문 : http://xmlsoft.org/tutorial/index.html

### Abstract

Libxml은 자유롭게 사용할 수 있는 라이센스로 제공되고, 다양한 플랫폼에서 사용할 수 있는 XML을 다루기 위한 C언어 라이브러리이다. 이 문서에서는 기본적인 기능들의 예제를 제공한다.

### Introduction

Libxml은 XML 데이터를 읽고, 쓰고, 다루기 위한 함수들을 구현한 C언어 라이브러리이다. 이 문서에서는 예제 코드와 기본적인 기능들에 대해서 설명한다. 완전한 문서와 더욱 자세한 사항에 대해서는 프로젝트 홈페이지에서 확인할 수 있다.

이 문서에서는 아래에 나열된 간단한 XML 프로그램들을 사용하여 설명한다.

- XML 문서 해석
- 특정 엘리먼트로부터 문자열 추출하기
- 엘리먼트와 내용을 추가하기
- 속성을 엘리먼트에 추가하기
- 속성값 추출하기

예제 프로그램의 전체 소스코드는 Appendix에서 찾을 수 있다.

### Data types

Libxml에서는 몇 가지 data type을 정의하고 있다.

- xmlChar : UTF-8로 인코딩된 character type이다. UTF-8이 아닐 경우 반드시 UTF-8로 변환하여 사용해야한다.
- xmlDoc : 해석된 XML 문서가 트리 구조로 저장될 수 있도록 마련된 구조체이다. xmlDocPtr은 xmlDoc 구조체의 포인터형이다.
- xmlNode : 하나의 노드를 저장하기 위한 구조체. xmlNodePtr은 xmlNode 구조체의 포인터형이다. xmlDoc의 트리구조를 탐색하는데 사용된다.

### Parsing the file

xml 파일을 불러와서 해석하고, 에러 검사를 하는데는 파일이름과 하나의 function만 있으면된다.

```cpp
xmlDocPtr doc; // (1)
xmlNodePtr cur; // (2)
doc = xmlParseFile(docname); // (3)
if(doc == NULL) { // (4)
    fprintf(stderr, "Document not parsed successfully.\n");
    return;
}
cur = xmlDocGetRootElement(doc); // (5)
if(cur == NULL) { // (6)
    fprintf(stderr, "empty document\n");
    xmlFreeDoc(doc);
    return;
}
if(xmlStrcmp(cur->name, (const xmlChar *)"story")) { // (7)
    fprintf(stderr, "document of the wrong type, root node != story");
    xmlFreeDoc(doc);
    return;
}
```

1. 해석된 문서를 가리킬 포인터 선언
2. 노드를 가리키기 위한 포인터 선언
3. docname의 문서를 불러와 해석한다.
4. 문서가 정상적으로 로드/해석 되었는지 확인한다.
5. root 엘리먼트를 찾는다.
6. 문서에 내용이 있는지 확인한다.
7. root 엘리먼트의 이름이 story인지 확인한다.

> Note : 이 예제에서 에러가 발생할 수 있는 것은 적절하지 않은 인코딩이다. XML 표준에서는 문서가 UTF-8 또는 UTF-16이 아닌 다른 인코딩으로 저장되어 있을 경우 명시적으로 해당 인코딩 타입을 기술하도록 되어 있다. 문서에 인코딩 타입이 기술되어 있다면, libxml은 자동적으로 해당 인코딩 타입에서 UTF-8로 변환한다. 자세한 XML 인코딩 requirement에 대해서는 XML 표준을 참조하라.

### Retrieving element content

엘리먼트의 내용을 추출하기 위해서는 문서 tree에서 해당 엘리먼트를 찾아야한다. 이 예제에서는 "story" 엘리먼트로부터 "keyword"라는 엘리먼트를 찾는다. 원하는 것을 찾기 위해서 tree를 하나하나 검색해야한다. doc(xmlDocPtr), cur(xmlNodePtr)은 이미 가지고 있다고 가정하고 설명한다.

```cpp
cur = cur->xmlChildrenNode; // (1)
while(cur != NULL) { // (2)
    if((!xmlStrcmp(cur->name, (const xmlChar *)"storyinfo"))) {
        parseStory(doc, cur);
    }
    cur = cur->next;
}
```

1. cur의 첫번째 자식 노드를 가져온다. 여기서 cur은 문서의 root 엘리먼트인 "story"이다. 즉, "story"의 첫번째 자식 엘리먼트를 가져오는 것이다.
2. 이 loop에서는 "story" 엘리먼트의 자식들 중에서 "storyinfo"인 엘리먼트를 찾는다. "storyinfo"가 아니면 다음 자식 엘리먼트로 이동하고, 찾으면 parseStory()를 호출한다.

```cpp
void parseStory(xmlDocPtr doc, xmlNodePtr cur) {
    xmlChar *key;
    cur = cur->xmlChildrenNode; // (1)
    while(cur != NULL) { // (2)
        if((!xmlStrcmp(cur->name, (const xmlChar *)"keyword"))) {
            key = xmlNodeListGetString(doc, cur->xmlChildrenNode, 1); // (3)
            printf("keyword: %s\n", key);
            xmlFree(key);
        }
        cur = cur->next;
    }
    return;
}
```

1. 첫 번째 자식 노드를 가지고온다.
2. 이전 코드의 loop 처럼 loop를 사용하여 자식 노드들 중에서 "keyword"라는 이름을 가진 노드를 찾는다.
3. "keyword" 노드를 찾으면 내용을 xmlNodeListGetString()을 사용해서 가져와 출력한다.

xmlNodeListGetString()을 호출할때 cur->xmlChildrenNode를 인자로 넘겨주는데, XML에서는 내용이 엘리먼트의 자식 노드로 표현이 되기 때문에 "keyword"의 자식노드들 중에서 문자열 데이터를 가져오기 위해서 자식 노드들 중에서 검색하는 것이다.

> Note. xmlNodeListGetString()은 메모리에 공간을 잡아서(할당하고) 문자열을 넣어 return하기 때문에 사용한 이후에 반드시 메모리를 해제해야만 한다.(xmlFree() 사용)

### Using xpath to retrieve element content

Libxml2에서는 문서 tree에서 엘리먼트를 탐색하기 위한 추가적인 방법인 XPath라는 것을 포함하고 있다. XPath는 문서에서 특정 노드를 찾기위한 표준적인 검색 방법을 제공한다.

> Note. XPath에 대해서 자세히 알고 싶다면 XPath 문서를 참고하자.

XPath를 사용하기 위해서는 xmlXPathContext를 설정하고, xmlXPathEvalExpression() 함수를 호출한다. 이 함수는 xmlXPathObjectPtr를 반환한다.

```cpp
xmlXPathObjectPtr getnodeset (xmlDocPtr doc, xmlChar *xpath) {
    xmlXPathContextPtr context; // (1)
    xmlXPathObjectPtr result;
    context = xmlXPathNewContext(doc); // (2)
    result = xmlXPathEvalExpression(xpath, context); // (3)
    if(xmlXPathNodeSetIsEmpty(result->nodesetval)) { // (4)
        printf("No result\n");
        return NULL;
    }
    xmlXPathFreeContext(context);
    return result;
}
```

1. 변수 선언
2. context 변수 초기화
3. XPath 표현식 적용
4. 결과 확인 & 메모리 해제

위 함수에서 반환되는 xmlXPathObjectPtr은 노드들과 반복적인 동작을 위한 정보들의 집합을 포함하고 있다. 노드 집합은 엘리먼트 개수(nodeNr)와 노드들의 배열(nodeTab)을 가지고 있다.

```cpp
for(i = 0; i < nodeset->nodeNr; i++) { // (1)
    keyword = xmlNodeListGetString(doc, nodeset->nodeTab[i]->xmlChildrenNode, 1); // (2)
    printf("keyword: %s\n", keyword);
    xmlFree(keyword);
}
```

1. nodeset->nodeNr은 노드 집합이 가지고 있는 엘리먼트 개수이다.
2. 각 노드의 내용을 추출하여 출력한다.

#### Writing element content

엘리먼트 내용을 추가하는 것은 이전에 이미 했던 과정들(문서를 해석하고, 노드들을 탐색)과 많은 부분이 동일하다. 문서를 불러와 해석하고, 원하는 노드를 찾고, 내용을 추가하면 된다. 여기서는 "storyinfo" 엘리먼트를 찾아서 keyword를 추가하고 파일로 저장한다.

```cpp
void parseStory(mxlDocPtr doc, xmlNodePtr cur, char *keyword) {
    xmlNewTextChild(cur, NULL, "keyword", keyword); // (1)
    return;
}
```

1. xmlNewTextChild 함수는 현재 노드에 새로운 자식 노드를 추가한다.

노드를 추가한 후에는 파일로 저장하기를 원할 것이다. 네임스페이스가 포함되어 저장되기를 원한다면 여기서 추가할 수 있다. 아래 예제에서는 네임스페이스가 NULL인 경우이다.

```cpp
xmlSaveFormatFile(docname, doc, 1);
```

첫번째 인자는 파일 이름이다. 읽어들인 파일명과 동일한 파일명을 입력하면 덮어쓰게 된다. 두번째 인자는 xmlDoc 구조체의 포인터이다. 세번째 인자를 1로 설정하면 indenting하여 저장한다.

#### Writing attribute

속성을 추가하는 것은 새 엘리먼트를 추가하는 것과 비슷하다. 이 예제에서는 libxml tutorial 문서의 URI를 추가한다.

추가할 위치는 story 엘리먼트의 child이다. 따라서 새로운 엘리먼트와 속성을 추가할 위치를 찾는 것을 간단하다.

먼저 변수를 선언한다.

```cpp
xmlAttrPtr newattr;
```

xmlNodePtr도 추가적으로 필요하다.

```cpp
xmlNodePtr newnode;
```

root 엘리먼트가 story이면, 다른 노드를 탐색하기 전까지는 cur이 root 엘리먼트를 가리키고 있다. 따라서 cur에 새 엘리먼트와 속성을 추가하면 된다.

```cpp
newnode = xmlNewTextChild(cur, NULL, "reference", NULL); // (1)
newattr = xmlNewProp(newnode, "uri", uri); // (2)
```

1. 먼저 새로운 노드를 현재 노드의 child로 xmlNewTextChild 함수를 사용해서 생성한다.
2. 생성된 노드에 새로운 속성을 추가한다.

앞의 예제와 같이 노드가 추가되면 파일에 저장한다.

#### Retrieving attributes

속성값을 추출하는 것은 노드에서 내용을 추출하는 이전의 예제와 거의 동일하다. 이 예제에서는 앞의 예제에서 추가했던 URI 속성의 값을 추출할 것이다.

```cpp
void getReference(xmlDocPtr doc, xmlNodePtr cur) {
    xmlChar *uri;
    cur = cur->xmlChildrenNode;
    while(cur != NULL) {
        if((!xmlStrcmp(cur->name, (const xmlChar *)"reference"))) {
            uri = xmlGetProp(cur, "uri"); // (1)
            printf("uri: %s\n", uri);
            xmlFree(uri);
        }
        cur = cur->next;
    }
    return;
}
```

1. 핵심 함수는 xmlGetProp()이다. 이 함수는 속성의 값을 xmlChar 형식으로 반환한다.

> Note. 만약 고정으로 선언된 DTD를 사용하거나 속성의 기본 값이 설정되어 있다면, 이 함수는 값을 추출할 것이다.

### Encoding conversion

데이터 인코딩 호환성 문제는 XML을 다루는데 있어 가장 어려운 문제중 하나이다. 이 문제를 회피하고 싶다면 어플리케이션을 디자인할때 내부적으로, libxml로 저장/관리되는 데이터에 대해서 UTF-8 사용을 고려하라. 프로그램에서 사용되는 다른 포맷으로 된 데이터(ISO-88590-1과 같은 데이터)는 libxml 함수들로 전달되기 전에 반드시 UTF-8로 변환되어야한다. 출력 데이터가 UTF-8이 아닌 다른 포맷을 원할 경우 역시 반드시 변환을 거쳐야 한다.

Libxml은 데이터 변환이 가능한 경우 iconv를 사용한다. iconv가 없을 경우 UTF-8과 UTF-16, ISO-8859-1만 사용될 수 있다. iconv가 있을 경우 어떤 포맷이라도 변환을 거쳐 사용할 수 있다. 현재 iconv는 150여가지의 포맷을 지원한다.

> Warning. 일반적으로 저지르기 쉬운 실수 중의 하나는, 하나의 코드 내, 다른 부분에서 사용되는 내부 데이터에 서로다른 포맷을 사용하는 것이다. 가장 흔한 경우가 libxml에서는 내부 데이터를 UTF-8로 가정하는데 libxml를 사용하는 어플리케이션에서는 내부 데이터를 ISO-8859-1로 가정하는 경우이다. 그 결과 어플리케이션 내부 데이터를 각 코드에서 다르게 실행하게 되므로 잘못 해석하는 경우가 발생할 수 있다.

이 예제는 간단한 문서를 구성하고, command line에서 입력되는 내용을 root 엘리먼트에 추가하고, 그 결과를 적절한 인코딩으로 stdout으로 내보낸다. 여기서는 ISO-8859-1 인코딩을 사용한다. command line에서 입력된 문자열은 ISO-8859-1에서 UTF-8로 변환된다. 예제에서 변환과 캡슐화를 위해 사용된 함수는 xmlFindCharEncodingHandler이다.

```cpp
xmlCharEncodingHandlerPtr handler; // (1)
size = (int)strlen(in) + 1; // (2)
out_size = size * 2 - 1;
out = malloc((size_t)out_size);
...
handler = xmlFindCharEncodingHandler(encoding); // (3)
...
handler->input(out, &out_size, in, &temp); // (4)
...
xmlSaveFormatFileEnc("-", doc, encoding, 1); // (5)
```

1. xmlCharEncodingHandler 함수를 위한 handler 포인터 선언
2. xmlCharEncodingHandler 함수는 입력과 출력의 크기를 필요로한다. 여기서 그 크기를 계산한다.
3. xmlFindCharEncodingHandler 함수는 인자로 초기 데이터 인코딩 타입을 받아 built-in 변환 핸들러를 검색하여 있으면 핸들러를 반환하고, 찾지 못한 경우 NULL을 반환한다.
4. 변환 함수는 인자로 입력과 출력 문자열에 대한 포인터와 각각의 크기를 필요로 한다. 크기정보는 반드시 이전에 계산 되어 있어야 한다.
5. 출력으로 UTF-8이 아닌 특정 인코딩 타입으로 원할 경우 xmlSaveFormatFileEnc 함수를 사용한다.

### Appendix

#### Compilation

Libxml에는 xml2-config 스크립트가 포함되어 있으며, 이것은 컴파일에 필요한 flag들을 생성해준다. pre-processor 및 컴파일 flags를 생성하기 위해서는 xml2-config --cflags를 사용하고, linking 작업에는 xml2-config --libs를 사용하라. 다른 옵션을 확인하고 싶으면 xml2-config --help를 입력하면 된다.

#### Sample document

```xml
<?xml version="1.0"?>
<story>
    <storyinfo>
        <author>John Fleck</author>
        <datewritten>June 2, 2002</datewritten>
        <keyword>example keyword</keyword>
    </storyinfo>
    <body>
        <headline>This is the headline</headline>
        <para>This is the body text.</para>
    </body>
</story>
```

#### Code for keyword example

```cpp
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <libxml/xmlmemory.h>
#include <libxml/parser.h>

void parseStory(xmlDocPtr doc, xmlNodePtr cur) {
    xmlChar *key;
    cur = cur->xmlChildrenNode;
    while(cur != NULL) {
        if((!xmlStrcmp(cur->name, (const xmlChar *)"keyword"))) {
            key = xmlNodeListGetString(doc, cur->xmlChildrenNode, 1);
            printf("keyword: %s\n", key);
            xmlFree(key);
        }
        cur = cur->next;
    }
    return;
}

static void parseDoc(char *docname) {
    xmlDocPtr doc;
    xmlNodePtr cur;
    doc = xmlParseFile(docname);
    if(doc == NULL) {
        fprintf(stderr, "Document not parsed successfully.\n");
        return;
    }
    cur = xmlDocGetRootElement(doc);
    if(cur == NULL) {
        fprintf(stderr, "empty document\n");
        xmlFreeDoc(doc);
        return;
    }
    if(xmlStrcmp(cur->name, (const xmlChar *)"story")) {
        fprintf(stderr, "document of the wrong type, root node != story\n");
        xmlFreeDoc(doc);
        return;
    }
    cur = cur->xmlChildrenNode;
    while(cur != NULL) {
        if((!xmlStrcmp(cur->name, (const xmlChar *)"storyinfo"))) {
            parseStory(doc, cur);
        }
        cur = cur->next;
    }
    xmlFreeDoc(doc);
    return;
}

int main(int argc, char **argv) {
    char *docname;
    if(argc <= 1) {
        printf("Usage: %s docname\n", argv[0]);
        return(0);
    }
    docname = argv[1];
    parseDoc(docname);
    return(1);
}
```

#### Code for xpath example

```cpp
#include <libxml/parser.h>
#include <libxml/xpath.h>

xmlDocPtr getdoc (char *docname) {
    xmlDocPtr doc;
    doc = xmlParseFile(docname);
    if (doc == NULL ) {
         fprintf(stderr,"Document not parsed successfully. \n");
        return NULL;
    }
    return doc;
}

xmlXPathObjectPtr getnodeset (xmlDocPtr doc, xmlChar *xpath) {
    xmlXPathContextPtr context;
    xmlXPathObjectPtr result;
    context = xmlXPathNewContext(doc);
    result = xmlXPathEvalExpression(xpath, context);
    if(xmlXPathNodeSetIsEmpty(result->nodesetval)) {
        printf("No result\n");
        return NULL;
    }
    xmlXPathFreeContext(context);
    return result;
}

int main(int argc, char **argv) {
    char *docname;
    xmlDocPtr doc;
    xmlChar *xpath = (xmlChar *)"//keyword";
    xmlNodeSetPtr nodeset;
    xmlXPathObjectPtr result;
    int i;
    xmlChar *keyword;
    if (argc <= 1) {
        printf("Usage: %s docname\n", argv[0]);
        return(0);
    }
    docname = argv[1];
    doc = getdoc(docname);
    result = getnodeset (doc, xpath);
    if (result) {
        nodeset = result->nodesetval;
        for (i=0; i < nodeset->nodeNr; i++) {
            keyword = xmlNodeListGetString(doc, nodeset->nodeTab[i]->xmlChildrenNode, 1);
            printf("keyword: %s\n", keyword);
            xmlFree(keyword);
        }
        xmlXPathFreeObject (result);
    }
    xmlFreeDoc(doc);
    xmlCleanupParser();
    return (1);
}
```

#### Code for add keyword example

```cpp
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <libxml/xmlmemory.h>
#include <libxml/parser.h>

void parseStory (xmlDocPtr doc, xmlNodePtr cur, char *keyword) {
    xmlNewTextChild (cur, NULL, "keyword", keyword);
    return;
}

xmlDocPtr parseDoc(char *docname, char *keyword) {
    xmlDocPtr doc;
    xmlNodePtr cur;
    doc = xmlParseFile(docname);
    if (doc == NULL ) {
        fprintf(stderr,"Document not parsed successfully. \n");
        return (NULL);
    }
    cur = xmlDocGetRootElement(doc);
    if (cur == NULL) {
        fprintf(stderr,"empty document\n");
        xmlFreeDoc(doc);
        return (NULL);
    }
    if (xmlStrcmp(cur->name, (const xmlChar *) "story")) {
        fprintf(stderr,"document of the wrong type, root node != story");
        xmlFreeDoc(doc);
        return (NULL);
    }
    cur = cur->xmlChildrenNode;
    while (cur != NULL) {
        if ((!xmlStrcmp(cur->name, (const xmlChar *)"storyinfo"))) {
            parseStory (doc, cur, keyword);
        }
        cur = cur->next;
    }
    return(doc);
}

int main(int argc, char **argv) {
    char *docname;
    char *keyword;
    xmlDocPtr doc;
    if (argc <= 2) {
        printf("Usage: %s docname, keyword\n", argv[0]);
        return(0);
    }
    docname = argv[1];
    keyword = argv[2];
    doc = parseDoc (docname, keyword);
    if (doc != NULL) {
        xmlSaveFormatFile (docname, doc, 0);
        xmlFreeDoc(doc);
    }
    return (1);
}
```

#### Code for add attribute example

```cpp
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <libxml/xmlmemory.h>
#include <libxml/parser.h>

xmlDocPtr parseDoc(char *docname, char *uri) {
    xmlDocPtr doc;
    xmlNodePtr cur;
    xmlNodePtr newnode;
    xmlAttrPtr newattr;
    doc = xmlParseFile(docname);
    if (doc == NULL ) {
        fprintf(stderr,"Document not parsed successfully. \n");
        return (NULL);
    }
    cur = xmlDocGetRootElement(doc);
    if (cur == NULL) {
        fprintf(stderr,"empty document\n");
        xmlFreeDoc(doc);
        return (NULL);
    }
    if (xmlStrcmp(cur->name, (const xmlChar *) "story")) {
        fprintf(stderr,"document of the wrong type, root node != story");
        xmlFreeDoc(doc);
        return (NULL);
    }
    newnode = xmlNewTextChild (cur, NULL, "reference", NULL);
    newattr = xmlNewProp (newnode, "uri", uri);
    return(doc);
}

int main(int argc, char **argv) {
    char *docname;
    char *uri;
    xmlDocPtr doc;
    if (argc <= 2) {
        printf("Usage: %s docname, uri\n", argv[0]);
        return(0);
    }
    docname = argv[1];
    uri = argv[2];
    doc = parseDoc (docname, uri);
    if (doc != NULL) {
        xmlSaveFormatFile (docname, doc, 1);
        xmlFreeDoc(doc);
    }
    return (1);
}
```

#### Code for retrieving attribute value example

```cpp
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <libxml/xmlmemory.h>
#include <libxml/parser.h>

xmlDocPtr parseDoc(char *docname, char *uri) {
    xmlDocPtr doc;
    xmlNodePtr cur;
    xmlNodePtr newnode;
    xmlAttrPtr newattr;
    doc = xmlParseFile(docname);
    if (doc == NULL ) {
        fprintf(stderr,"Document not parsed successfully. \n");
        return (NULL);
    }
    cur = xmlDocGetRootElement(doc);
    if (cur == NULL) {
        fprintf(stderr,"empty document\n");
        xmlFreeDoc(doc);
        return (NULL);
    }
    if (xmlStrcmp(cur->name, (const xmlChar *) "story")) {
        fprintf(stderr,"document of the wrong type, root node != story");
        xmlFreeDoc(doc);
        return (NULL);
    }
    newnode = xmlNewTextChild (cur, NULL, "reference", NULL);
    newattr = xmlNewProp (newnode, "uri", uri);
    return(doc);
}

int main(int argc, char **argv) {
    char *docname;
    char *uri;
    xmlDocPtr doc;
    if (argc <= 2) {
        printf("Usage: %s docname, uri\n", argv[0]);
        return(0);
    }
    docname = argv[1];
    uri = argv[2];
    doc = parseDoc (docname, uri);
    if (doc != NULL) {
        xmlSaveFormatFile (docname, doc, 1);
        xmlFreeDoc(doc);
    }
    return (1);
}
```

#### Code for encoding conversion example

```cpp
#include <string.h>
#include <libxml/parser.h>

unsigned char* convert (unsigned char *in, char *encoding) {
    unsigned char *out;
    int ret,size,out_size,temp;
    xmlCharEncodingHandlerPtr handler;
    size = (int)strlen(in)+1;
    out_size = size*2-1;
    out = malloc((size_t)out_size);
    if (out) {
        handler = xmlFindCharEncodingHandler(encoding);
        if (!handler) {
            free(out);
            out = NULL;
        }
    }
    if (out){
        temp=size-1;
        ret = handler->input(out, &out_size, in, &temp);
        if (ret || temp-size+1) {
            if (ret) {
                printf("conversion wasn't successful.\n");
            }
            else {
                printf("conversion wasn't successful. converted\n");
            }
            free(out);
            out = NULL;
        }
        else {
            out = realloc(out,out_size+1);
            out[out_size]=0; /*null terminating out*/
        }
    }
    else {
        printf("no mem\n");
    }
    return (out);
}

int main(int argc, char **argv) {
    unsigned char *content, *out;
    xmlDocPtr doc;
    xmlNodePtr rootnode;
    char *encoding = "ISO-8859-1";
    if (argc <= 1) {
        printf("Usage: %s content\n", argv[0]);
        return(0);
    }
    content = argv[1];
    out = convert(content, encoding);
    doc = xmlNewDoc ("1.0");
    rootnode = xmlNewDocNode(doc, NULL, (const xmlChar*)"root", out);
    xmlDocSetRootElement(doc, rootnode);
    xmlSaveFormatFileEnc("-", doc, encoding, 1);
    return (1);
}
```

---

Date: 2026. 03. 15

Tags: libxml, tutorial, 번역
