<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link href="//cdn.bootcss.com/chartist/0.10.1/chartist.min.css" rel="stylesheet">
    <script src="//cdn.bootcss.com/chartist/0.10.1/chartist.min.js"></script>
    <script src="//cdn.bootcss.com/jquery/3.1.1/jquery.min.js"></script>
    <title>Title</title>
</head>
<body>
<button>Update the Chart!</button>
<div class="ct-chart ct-perfect-fourth"></div>
<script type="text/javascript">
    var chart;
    var getData = $.get('/data');
    // done 相当于 success 方法
    getData.done(function (results) {
        var data = {
            // A labels array that can contain any sort of values
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
            // Our series array that contains series objects or in this case series data arrays
            series: [
                results.results
            ]
        };

        // As options we currently only set a static size of 300x200 px. We can also omit this and use aspect ratio containers
        // as you saw in the previous example
        var options = {
            width: 800,
            height: 600
        };

作者：与蟒唯舞
链接：https://www.jianshu.com/p/6c9d0dcd3382
來源：简书
简书著作权归作者所有，任何形式的转载都请联系作者获得授权并注明出处。