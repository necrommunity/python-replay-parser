$(function(){
    console.log("loaded");
    $.ajaxSetup({
        scriptCharset: "utf-8",
        contentType: "application/json; charset=utf-8"
    });
    var jqxhr = $.getJSON("data.json",{}, function(){
    })
        .done(function(data){
            // do a bunch of stuff here
            totalWins = 0;
            totalRuns = 0;
            totalTime = 0;
            totalWinTime = 0;
            charWins = {}
            charDeaths = {}
            headers = [
                "Date",
                "Character",
                "Seed",
                "Ending Zone",
                "Run Time",
                "Win",
                "Key Presses",
                "Songs", 
                "File"
            ];
            totalRuns = data["data"].length
            $.each(data["data"], function(i, item){
                
            //     output = output + "<tr class=\"\">";
            //     output = output + "<td scope=\"row\" class=\"td\">" + moment(item.runDate*1000).format("YYYY/MM/DD HH:mm:ss") + "</td>";
            //     output = output + "<td class=\"td\">" + item.fChar1 + "</td>";
            //     output = output + "<td class=\"td\">" + item.seed + "</td>";
            //     output = output + "<td class=\"td\">" + item.endZone + "</td>";
            //     output = output + "<td class=\"td\">" + item.fRunTime+ "</td>";
            //     if (item.win == true) {
            //         output = output + "<td class=\"td bg-success\"> Yes </td>";
            //     } else {
            //         output = output + "<td class=\"td bg-danger\"> No </td>";
            //     }
            //     output = output + "<td class=\"td\">" + item.keyPresses + "</td>";
            //     output = output + "<td class=\"td\">" + item.songs + "</td>";
            //     output = output + "<td class=\"td\">" + item.file + "</td>";
            //     output = output + "</tr>";
                totalTime += item.runTime;
                if (item.win === true) {
                    if ( $.inArray(item.fChar1, $.map(charWins, function(element,index) {return index})) >= 0) {
                        charWins[item.fChar1] += 1;
                    } else {
                        charWins[item.fChar1] = 1;
                    }
                    totalWins += 1;
                    totalWinTime += item.runTime;
                } else {
                    if ( $.inArray(item.fChar1, $.map(charDeaths, function(element,index) {return index})) >= 0) {
                        charDeaths[item.fChar1] += 1;
                    } else {
                        charDeaths[item.fChar1] = 1;
                    }
                }
            });
            console.log(totalRuns, totalWins, totalRuns - totalWins, totalTime, totalWinTime, charWins, charDeaths);
            dataWins = [];
            $.each(charWins, function(i, n) {
                dataWins.push({"y": Math.round(n/totalWins*100.00, 2), "label": i});
            });
            dataDeaths = [];
            $.each(charDeaths, function(i, n) {
                dataDeaths.push({"y": Math.round(n/(totalRuns - totalWins)*100, 2), "label": i});
            });
            // output = output + "</tbody>";
            // output = output + "<tfoot>";
            // output = output + "</tfoot>";
            // output = output + "</table>";


            // $('#table').html(output);
            // $('#output_table').DataTable({
            //     paging: false,
            //     order: [0, "desc"]
            // });
            // $('#wins').html("Total Wins: " + totalWins);
            // $('#runs').html("Total Runs: " + totalRuns);
            
            var options = {
                title: {
                    text: "Wins"
                },
                subtitles: [{
                    text: ""
                }],
                animationEnabled: true,
                data: [{
                    type: "pie",
                    startAngle: 40,
                    toolTipContent: "<b>{label}</b>: {y}%",
                    showInLegend: "true",
                    legendText: "{label}",
                    indexLabelFontSize: 16,
                    indexLabel: "{label} - {y}%",
                    dataPoints: dataWins
                }]
            };
            $("#winsChart").CanvasJSChart(options);
                        
            var options = {
                title: {
                    text: "Deaths"
                },
                subtitles: [{
                    text: ""
                }],
                animationEnabled: true,
                data: [{
                    type: "pie",
                    startAngle: 40,
                    toolTipContent: "<b>{label}</b>: {y}%",
                    showInLegend: "true",
                    legendText: "{label}",
                    indexLabelFontSize: 16,
                    indexLabel: "{label} - {y}%",
                    dataPoints: dataDeaths
                }]
            };
            $("#deathsChart").CanvasJSChart(options);
            
        });

});