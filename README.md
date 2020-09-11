# Stack_Overflow_NN_Search
Sementic search problem search similar asked question.

The problem based on sementic search similarity as discussed by Applied AI public live session <a href='https://www.youtube.com/watch?v=FpMmpKIvsnQ&ab_channel=AppliedAICourse'> here is the link </a> In which we have given a question asked by user and we have to capture k similar question to it. Applied AI public live session explain this in very detailed way, I strongly recommend to please go through the series of this video in order to understand whole flow. Now coming back to point How we wil do that. This code is devided into 3 parts.

<li> Elastic search DB</li>
<li> sentence vector Model</li>
<li> search Service</li>

<h3> 1.Elastic search DB</h3>
This is simple Elastic search Instance running on the same machine or different machine.

<h3> 2.sentence vector Model: </h3>

This Module Contain flask Based API to get Sentence vector of given sentence by using Universal Sentence Encoder(USE) model. It' s a good practice to download the model locally and put it into /sentencevectormodel/USEModel folder so that It need not download every time from server.If It will not find the model It will Go and Fetch the model from server path given inside sentencevectormodel.py in USE_URL. Here I used USE model but if you want you can choose any sentence to vector model based on your preference, you need to change a code little bit. As the flask app started It loads the model and keep it into local variable, later If some request will come with the list of sentence that need to encoded it use this model to generate vector of each sentence and sent it to user. Publiccly expose API

```
URI- 127.0.0.1:5000/use/getsentencevector
Type:- POST
BODY: { "sentences": ["sentence that need to Encode"]} // for more sentence just add sentence to list
Response : [[....512 float number represent sentence vector... ]]
```

<h3> 3.search Service:</h3><br/>
This is main API which gives the actual similar searched sentences with full Information.In this folder we have:<br/>
config folder : contains 3 json configuration file relative to searchservice folder<br/>
constant.json:-<br/>
```json
{
  "questionMapping": "path in which question.csv file column map to elastic search DB while creating question-index e.g:- \"./DBMapping/questionmapping.json\""
}
```

esconfig.json:-<br/>
```json
{
  "elasticSearchHost":  "server IP where elastic search DB is located (download from https://www.elastic.co/ put it in server and start it) (e.g:-\"localhost\")",
  "elasticSearchPort": "port in which elastic search is running (e.g:-9200)"
}
```
  
textvectorconfig.json:-  <br/>
```json
{
  "textVectorPOSTAPI": "API in which getsentencevector flask API is running"
}
```
Data:- folder contain answer.csv, question.csv and tag.csv file available in <a href='https://www.kaggle.com/stackoverflow/stacksample'>this link</a>

DBMapping:- contain 3 json file which is used while creating index in elastic DB<br/>
<li>answermapping.json:- used while creating indexes for answer.csv</li>
<li>questionmapping.json:- used while creating indexes for question.csv</li>
<li>tagmapping.json:- used while creating indexes for tag.csv</li>

modules:- contain python helper file which is used by flask main.py

APIrequest.py:- Used to make Http calls related class which helps us to make call for getting sentence vector

elasticsearchconnection.py:- used to get elastic search connection object

essearch.py:- used to get search result from query question

indexcreation.py:- used to create index for question, answer and tag and insert into elastic DB

test.py:- simple testing any method or debugg file.

main.py:- flask main entry point

``` 
APIs
URI- 127.0.0.1/5001/es-search/get-answer
Type:- GET
ARGS: ?questionId=question Id 
Response :  // for  http://127.0.0.1:5001/es-search/get-answer/?questionId=580
```

```json
    {
  "_shards": {
    "failed": 0,
    "skipped": 0,
    "successful": 1,
    "total": 1
  },
  "hits": {
    "hits": [
      {
        "_id": "585",
        "_index": "answer-index",
        "_score": 1.0,
        "_source": {
          "body": "<p>For my projects I alternate between SQL Compare from REd Gate and the Database Publishing Wizard from Microsoft which you can download free\n<a href=\"http://www.microsoft.com/downloads/details.aspx?familyid=56E5B1C5-BF17-42E0-A410-371A838E570A&amp;displaylang=en\">here</a>.</p>\n\n<p>The Wizard isn't as slick as SQL Compare or SQL Data Compare but it does the trick. One issue is that the scripts it generates may need some rearranging and/or editing to flow in one shot.</p>\n\n<p>On the up side, it can move your schema and data which isn't bad for a free tool.</p>",
          "creationDate": "2008-08-02T23:40:04Z",
          "id": 585,
          "ownerUserId": 149,
          "parentId": 580,
          "score": 13
        },
        "_type": "_doc"
      },
      {
        "_id": "586",
        "_index": "answer-index",
        "_score": 1.0,
        "_source": {
          "body": "<p>I've taken to hand-coding all of my DDL (creates/alter/delete) statements, adding them to my .sln as text files, and using normal versioning (using subversion, but any revision control should work). This way, I not only get the benefit of versioning, but updating live from dev/stage is the same process for code and database - tags, branches and so on work all the same.</p>\n\n<p>Otherwise, I agree redgate is expensive if you don't have a company buying it for you. If you can get a company to buy it for you though, it really is worth it!</p>",
          "creationDate": "2008-08-02T23:51:09Z",
          "id": 586,
          "ownerUserId": 34,
          "parentId": 580,
          "score": 17
        },
        "_type": "_doc"
      },
      {
        "_id": "590",
        "_index": "answer-index",
        "_score": 1.0,
        "_source": {
          "body": "<p>If you have a company buying it, Toad from Quest Software has this kind of management functionality built in.  It's basically a two-click operation to compare two schemas and generate a sync script from one to the other.</p>\n\n<p>They have editions for most of the popular databases, including of course Sql Server.</p>",
          "creationDate": "2008-08-03T00:22:03Z",
          "id": 590,
          "ownerUserId": 116,
          "parentId": 580,
          "score": 2
        },
        "_type": "_doc"
      },
      {
        "_id": "591",
        "_index": "answer-index",
        "_score": 1.0,
        "_source": {
          "body": "<p>I work the same way Karl does, by keeping all of my SQL scripts for creating and altering tables in a text file that I keep in source control.  In fact, to avoid the problem of having to have a script examine the live database to determine what ALTERs to run, I usually work like this:</p>\n\n<ul>\n<li>On the first version, I place everything during testing into one SQL script, and treat all tables as a CREATE.  This means I end up dropping and readding tables a lot during testing, but that's not a big deal early into the project (since I'm usually hacking the data I'm using at that point anyway).</li>\n<li>On all subsequent versions, I do two things: I make a new text file to hold the upgrade SQL scripts, that contain just the ALTERs for that version.  And I make the changes to the original, create a fresh database script as well.  This way an upgrade just runs the upgrade script, but if we have to recreate the DB we don't need to run 100 scripts to get there.</li>\n<li>Depending on how I'm deploying the DB changes, I'll also usually put a version table in the DB that holds the version of the DB.  Then, rather than make any human decisions about which scripts to run, whatever code I have running the create/upgrade scripts uses the version to determine what to run.</li>\n</ul>\n\n<p>The one thing this will not do is help if part of what you're moving from test to production is data, but if you want to manage structure and not pay for a nice, but expensive DB management package, is really not very difficult.  I've also found it's a pretty good way of keeping mental track of your DB.</p>",
          "creationDate": "2008-08-03T00:37:03Z",
          "id": 591,
          "ownerUserId": 111,
          "parentId": 580,
          "score": 3
        },
        "_type": "_doc"
      },
      {
        "_id": "597",
        "_index": "answer-index",
        "_score": 1.0,
        "_source": {
          "body": "<p>I agree that scripting everything is the best way to go and is what I advocate at work.  You should script everything from DB and object creation to populating your lookup tables.</p>\n\n<p>Anything you do in UI only won't translate (especially for changes... not so much for first deployments) and will end up requiring a tools like what Redgate offers.</p>",
          "creationDate": "2008-08-03T01:38:02Z",
          "id": 597,
          "ownerUserId": 76,
          "parentId": 580,
          "score": 1
        },
        "_type": "_doc"
      },
      {
        "_id": "1446",
        "_index": "answer-index",
        "_score": 1.0,
        "_source": {
          "body": "<p>Using SMO/DMO, it isn't too difficult to generate a script of your schema.  Data is a little more fun, but still doable.</p>\n\n<p>In general, I take \"Script It\" approach, but you might want to consider something along these lines:</p>\n\n<ul>\n<li>Distinguish between Development and Staging, such that you can Develop with a subset of data ... this I would create a tool to simply pull down some production data, or generate fake data where security is concerned.</li>\n<li>For team development, each change to the database will have to be coordinated amongst your team members.  Schema and data changes can be intermingled, but a single script should enable a given feature.  Once all your features are ready, you bundle these up in a single SQL file and run that against a restore of production.</li>\n<li>Once your staging has cleared acceptance, you run the single SQL file again on the production machine.</li>\n</ul>\n\n<p>I have used the Red Gate tools and they are <strong>great</strong> tools, but if you can't afford it, building the tools and working this way isn't too far from the ideal.</p>",
          "creationDate": "2008-08-04T17:38:59Z",
          "id": 1446,
          "ownerUserId": 307,
          "parentId": 580,
          "score": 2
        },
        "_type": "_doc"
      },
      {
        "_id": "1464",
        "_index": "answer-index",
        "_score": 1.0,
        "_source": {
          "body": "<p>Like Rob Allen, I use SQL Compare / Data Compare by Redgate. I also use the Database publishing wizard by Microsoft. I also have a console app I wrote in C# that takes a sql script and runs it on a server. This way you can run large scripts with 'GO' commands in it from a command line or in a batch script.</p>\n\n<p>I use Microsoft.SqlServer.BatchParser.dll and Microsoft.SqlServer.ConnectionInfo.dll libraries in the console application.</p>\n",
          "creationDate": "2008-08-04T18:00:50Z",
          "id": 1464,
          "ownerUserId": 26,
          "parentId": 580,
          "score": 5
        },
        "_type": "_doc"
      },
      {
        "_id": "9963",
        "_index": "answer-index",
        "_score": 1.0,
        "_source": {
          "body": "<p>I agree with keeping everything in source control and manually scripting all changes.  Changes to the schema for a single release go into a script file created specifically for that release.  All stored procs, views, etc should go into individual files and treated just like .cs or .aspx as far as source control goes.  I use a powershell script to generate one big .sql file for updating the programmability stuff.</p>\n\n<p>I don't like automating the application of schema changes, like new tables, new columns, etc.  When doing a production release, I like to go through the change script command by command to make sure each one works as expected.  There's nothing worse than running a big change script on production and getting errors because you forgot some little detail that didn't present itself in development.</p>\n\n<p>I have also learned that indexes need to be treated just like code files and put into source control.</p>\n\n<p>And you should definitely have more than 2 databases - dev and live.  You should have a dev database that everybody uses for daily dev tasks.  Then a staging database that mimics production and is used to do your integration testing.  Then maybe a complete recent copy of production (restored from a full backup), if that is feasible, so your last round of installation testing goes against something that is as close to the real thing as possible.</p>\n",
          "creationDate": "2008-08-13T15:41:44Z",
          "id": 9963,
          "ownerUserId": 1219,
          "parentId": 580,
          "score": 1
        },
        "_type": "_doc"
      },
      {
        "_id": "14447",
        "_index": "answer-index",
        "_score": 1.0,
        "_source": {
          "body": "<p>Don't forget Microsoft's solution to the problem: <a href=\"http://msdn.microsoft.com/en-gb/vsts2008/products/bb933747.aspx\" rel=\"nofollow\">Visual Studio 2008 Database Edition</a>.  Includes tools for deploying changes to databases, producing a diff between databases for schema and/or data changes, unit tests, test data generation.</p>\n\n<p>It's pretty expensive but I used the trial edition for a while and thought it was brilliant.  It makes the database as easy to work with as any other piece of code.</p>\n",
          "creationDate": "2008-08-18T10:47:50Z",
          "id": 14447,
          "ownerUserId": 1073,
          "parentId": 580,
          "score": 6
        },
        "_type": "_doc"
      },
      {
        "_id": "28410",
        "_index": "answer-index",
        "_score": 1.0,
        "_source": {
          "body": "<p>I do all my database creation as DDL and then wrap that DDL into a schema maintainence class. I may do various things to create the DDL in the first place but fundamentally I do all the schema maint in code. This also means that if one needs to do non DDL things that don't map well to SQL you can write procedural logic and run it between lumps of DDL/DML.</p>\n\n<p>My dbs then have a table which defines the current version so one can code a relatively straightforward set of tests:</p>\n\n<ol>\n<li>Does the DB exist? If not create it.</li>\n<li>Is the DB the current version? If not then run the methods, in sequence, that bring the schema up to date (you may want to prompt the user to confirm and - ideally - do backups at this point).</li>\n</ol>\n\n<p>For a single user app I just run this in place, for a web app we currently to lock the user out if the versions don't match and have a stand alone schema maint app we run. For multi-user it will depend on the particular environment.</p>\n\n<p>The advantage? Well I have a very high level of confidence that the schema for the apps that use this methodology is consistent across all instances of those applications. Its not perfect, there are issues, but it works...</p>\n\n<p>There are some issues when developing in a team environment but that's more or less a given anyway!</p>\n\n<p>Murph</p>\n",
          "creationDate": "2008-08-26T15:38:22Z",
          "id": 28410,
          "ownerUserId": 1070,
          "parentId": 580,
          "score": 0
        },
        "_type": "_doc"
      },
      {
        "_id": "28698",
        "_index": "answer-index",
        "_score": 1.0,
        "_source": {
          "body": "<p>I'm using Subsonic's migrations mechanism so I just have a dll with classes in squential order that have 2 methods, up and down. There is a continuous integration/build script hook into nant, so that I can automate the upgrading of my database.</p>\n\n<p>Its not the best thign in the world, but it beats writing DDL.</p>\n",
          "creationDate": "2008-08-26T17:39:20Z",
          "id": 28698,
          "ownerUserId": 1220,
          "parentId": 580,
          "score": 1
        },
        "_type": "_doc"
      },
      {
        "_id": "31405",
        "_index": "answer-index",
        "_score": 1.0,
        "_source": {
          "body": "<p><a href=\"http://www.red-gate.com/products/SQL_Compare/index.htm\" rel=\"nofollow\">RedGate SqlCompare</a> is a way to go in my opinion. We do DB deployment on a regular basis and since I started using that tool I have never looked back. \nVery intuitive interface and saves a lot of time in the end.</p>\n\n<p>The Pro version will take care of scripting for the source control integration as well.</p>\n",
          "creationDate": "2008-08-28T00:22:08Z",
          "id": 31405,
          "ownerUserId": 3241,
          "parentId": 580,
          "score": 1
        },
        "_type": "_doc"
      },
      {
        "_id": "322859",
        "_index": "answer-index",
        "_score": 1.0,
        "_source": {
          "body": "<p>I'm currently working the same thing to you. Not only deploying SQL Server databases from test to live but also include the whole process from Local -> Integration -> Test -> Production. So what can make me easily everyday is I do <a href=\"http://tech.wowkhmer.com/post/2008/11/11/NAnt-task-with-Red-Gate-SQL-Compare.aspx\" rel=\"nofollow\">NAnt task with Red-Gate SQL Compare</a>. I'm not working for RedGate but I have to say it is good choice.</p>\n",
          "creationDate": "2008-11-27T03:15:45Z",
          "id": 322859,
          "ownerUserId": 35719,
          "parentId": 580,
          "score": 0
        },
        "_type": "_doc"
      },
      {
        "_id": "3001482",
        "_index": "answer-index",
        "_score": 1.0,
        "_source": {
          "body": "<p>I also maintain scripts for all my objects and data. For deploying I wrote this free utility - <a href=\"http://www.sqldart.com\" rel=\"nofollow\">http://www.sqldart.com</a>. It'll let you reorder your script files and will run the whole lot within a transaction.</p>\n",
          "creationDate": "2010-06-08T21:33:36Z",
          "id": 3001482,
          "ownerUserId": 346593,
          "parentId": 580,
          "score": 1
        },
        "_type": "_doc"
      }
    ],
    "max_score": 1.0,
    "total": {
      "relation": "eq",
      "value": 14
    }
    },
    "timed_out": false,
    "took": 2266
    }
```

```
URI- 127.0.0.1:5001/es-search/get-tag
Type:- GET
ARGS: ?questionId=question Id 
Response :  // for  http://127.0.0.1:5001/es-search/get-tag/?questionId=580
``` 

```json
    {
    "_shards": {
        "failed": 0,
        "skipped": 0,
        "successful": 1,
        "total": 1
    },
    "hits": {
        "hits": [
            {
                "_id": "25",
                "_index": "tag-index",
                "_score": 1.0,
                "_source": {
                    "id": 25,
                    "questionId": 580,
                    "tag": "sql-server"
                },
                "_type": "_doc"
            },
            {
                "_id": "26",
                "_index": "tag-index",
                "_score": 1.0,
                "_source": {
                    "id": 26,
                    "questionId": 580,
                    "tag": "sql-server-2005"
                },
                "_type": "_doc"
            },
            {
                "_id": "27",
                "_index": "tag-index",
                "_score": 1.0,
                "_source": {
                    "id": 27,
                    "questionId": 580,
                    "tag": "deployment"
                },
                "_type": "_doc"
            },
            {
                "_id": "28",
                "_index": "tag-index",
                "_score": 1.0,
                "_source": {
                    "id": 28,
                    "questionId": 580,
                    "tag": "release-management"
                },
                "_type": "_doc"
            }
        ],
        "max_score": 1.0,
        "total": {
            "relation": "eq",
            "value": 4
        }
    },
    "timed_out": false,
    "took": 69
    }
```
    
```    
URI- 127.0.0.1:5001/es-search/search-sentence
Type:- POST
BODY: raw JSON  {
    "sentence": "classification from api", // match pattern sentence
    "size": 5, // Number of matched queries // limited to 10
    "withAnswer": false, // If each query result contain with answer
    "withTag": false // If each query result contain tags
}
Response :  // for   http://127.0.0.1:5001/es-search/search-sentence
```

```json
    [
    {
        "body": "<p>In <code>weka.classifier.Evaluation</code> there is the <code>toMatrixString()</code> method, which outputs the confusion matrix like below.</p>\n\n<pre><code>  a  b  c   &lt;-- classified as\n 50  0  0 |  a = Iris-setosa\n  0 45  5 |  b = Iris-versicolor\n  0  3 47 |  c = Iris-virginica\n</code></pre>\n\n<p>I noticed classes in this output are taken from the dataset given as  parameter of <code>Evaluation</code> constructor. </p>\n\n<p>Is there a way to obtain a list of possible outputs from the <code>Classifier</code> object?</p>\n",
        "closedDate": null,
        "creationDate": "2015-11-17T15:51:43Z",
        "id": 33761280,
        "keywordScore": 2.0,
        "nnScore": null,
        "ownerUserId": 5296123,
        "score": 1,
        "title": "Weka API - possible classification output"
    },
    {
        "body": "<p>I'm trying to get good accuracy using WEKA and its classification options.</p>\n\n<p>by using this method I can not cover all options and this is why I'm afraid I could miss the optimal classification to get the best J48 tree solution.</p>\n\n<p>I have tried using number of classifications and methods such as (NB, costSensitive, attributeClassifier, etc..) and each of this have at least few options..</p>\n\n<p>My question is:</p>\n\n<p>is there any option to let the software (WEKA or other software) to run (even days!!) in order to find the best classification for optimal solution?\nIf to be more specific, could I determine the confusion matrix I would like to have and the software will tell me which classification or options to use?</p>\n",
        "closedDate": null,
        "creationDate": "2013-12-15T13:29:50Z",
        "id": 20595080,
        "keywordScore": 1.7530547919536288,
        "nnScore": null,
        "ownerUserId": 2737817,
        "score": 0,
        "title": "Optimal classification"
    },
    {
        "body": "<p>I am using <code>randomForest</code> package in R platform for classification task. </p>\n\n<pre><code>rf_object&lt;-randomForest(data_matrix, label_factor, cutoff=c(k,1-k))\n</code></pre>\n\n<p>where k ranges from 0.1 to 0.9.</p>\n\n<pre><code>pred &lt;- predict(rf_object,test_data_matrix)\n</code></pre>\n\n<p>I have the output from the random forest classifier and I compared it with the labels. So, I have the performance measures like accuracy, MCC, sensitivity, specificity, etc for 9 cutoff points.</p>\n\n<p>Now, I want to plot the ROC curve and obtain the area under the ROC curve to see how good the performance is. Most of the packages in R (like ROCR, pROC) require prediction and labels but I have sensitivity (TPR) and specificity (1-FPR).</p>\n\n<p>Can any one suggest me if the cutoff method is correct or reliable to produce ROC curve?\nDo you know any way to obtain ROC curve and area under the curve using TPR and FPR?</p>\n\n<p>I also tried to use the following command to train random forest. This way the predictions were continuous and were acceptable to <code>ROCR</code> and <code>pROC</code> packages in R. But, I am not sure if this is correct way to do. Can any one suggest me about this method?</p>\n\n<pre><code>rf_object &lt;- randomForest(data_matrix, label_vector)\npred &lt;- predict(rf_object, test_data_matrix)\n</code></pre>\n\n<p>Thank you for your time reading my problem! I have spent long time surfing for this. Thank you for your suggestion/advice.</p>\n",
        "closedDate": null,
        "creationDate": "2012-09-11T13:19:29Z",
        "id": 12370670,
        "keywordScore": 1.7420238358962759,
        "nnScore": null,
        "ownerUserId": 1662898,
        "score": 4,
        "title": "ROC curve for classification from randomForest"
    },
    {
        "body": "<p>I'm using Weka for text classification task.\nI created my data.arff File. It contains two attributes:</p>\n\n<ol>\n<li>text attribute</li>\n<li>class attribute</li>\n</ol>\n\n<p>Then, the generated ARFF file is processed with the StringToWordVector:</p>\n\n<blockquote>\n  <p>java weka.filters.unsupervised.attribute.StringToWordVector -i data/weather.arff -o data/out.arff\n  Then, NaiveBayes is used:\n  java weka.classifiers.bayes.NaiveBayes -t data/out.arff -K</p>\n</blockquote>\n\n<p>I have this problem:</p>\n\n<blockquote>\n  <p>weka.core.UnsupportedAttributeTypeException: weka.classifiers.bayes.NaiveBayes: Cannot handle numeric class!\n      at weka.core.Capabilities.test(Capabilities.java:954)\n      at weka.core.Capabilities.test(Capabilities.java:1110)\n      at weka.core.Capabilities.test(Capabilities.java:1023)\n      at weka.core.Capabilities.testWithFail(Capabilities.java:1302)\n      at weka.classifiers.bayes.NaiveBayes.buildClassifier(NaiveBayes.java:213)\n      at weka.classifiers.Evaluation.evaluateModel(Evaluation.java:1076)\n      at weka.classifiers.Classifier.runClassifier(Classifier.java:312)\n      at weka.classifiers.bayes.NaiveBayes.main(NaiveBayes.java:944)\n      at sun.reflect.NativeMethodAccessorImpl.invoke0(Native Method)\n      at sun.reflect.NativeMethodAccessorImpl.invoke(Unknown Source)\n      at sun.reflect.DelegatingMethodAccessorImpl.invoke(Unknown Source)\n      at java.lang.reflect.Method.invoke(Unknown Source)\n      at weka.gui.SimpleCLIPanel$ClassRunner.run(SimpleCLIPanel.java:265)</p>\n</blockquote>\n\n<p>Could anyone help me?\nI'm stuck at this level.</p>\n",
        "closedDate": null,
        "creationDate": "2012-03-04T18:30:41Z",
        "id": 9557650,
        "keywordScore": 1.7359921547929051,
        "nnScore": null,
        "ownerUserId": 1149602,
        "score": 0,
        "title": "Classification with Weka+ NaiveBayes Classifier+ Text classification"
    },
    {
        "body": "<p>I'm working on a project that requires categorizing content of a given URL. Basically, I want to pass a URL to this API and it will return the category or list of categories based on its content. I think Textwise.com may have this service. Are there other similar services out there?</p>\n",
        "closedDate": "2016-03-12T02:32:23Z",
        "creationDate": "2011-04-28T22:30:12Z",
        "id": 5825780,
        "keywordScore": null,
        "nnScore": 1.7182553,
        "ownerUserId": 225195,
        "score": 3,
        "title": "Semantic/Contextual Categorization API"
    }
    ]
```

So that is the sample project I created within less then a week.It still need some Improvement like making wach 3 module
completely decouple, it still contain some tight coupling in indexcreation.py and sentencevectormodel.py since it uses this modult to get sentence vector. I choose to do it because If I did this through API it will take more time to insert in elastic search DB, But If you need complete decouple model of all three so that they can be containerize and deployed in different system. you are free to do modification by your own the line number 374 where I am fetching sentence vector replace it with API call to get it as I did in _get_sentence_vector method in essearch.py you can replace it with this.
And remove all the direct import from any class used from sentencevectormodel.py as in test.py  then you are good to go.
Feel free to suggest any Improvement.<br/>
..Happy Learning...
