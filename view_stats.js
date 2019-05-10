$(function () {
    console.log("loaded");
    $.ajaxSetup({
        scriptCharset: "utf-8",
        contentType: "application/json; charset=utf-8"
    });
    var jqxhr = $.getJSON("data.json", {}, function () {
    })
        .done(function (data) {
            // do a bunch of stuff here
            totalWins = 0;
            totalRuns = 0;
            totalTime = 0;
            totalWinTime = 0;
            charWins = {}
            charDeaths = {}
            charTime = {}
            charFastest = {}
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
            $.each(data["data"], function (i, item) {
                totalTime += item.runTime;
                if (item.win === true) {
                    if ($.inArray(item.fChar1, $.map(charWins, function (element, index) { return index })) >= 0) {
                        charWins[item.fChar1] += 1;

                    } else {
                        charWins[item.fChar1] = 1;

                    }
                    totalWins += 1;
                    totalWinTime += item.runTime;
                    if ($.inArray(item.fChar1, $.map(charTime, function (element, index) { return index })) >= 0) {
                        charTime[item.fChar1]["times"].push(item.runTime);
                        charTime[item.fChar1]["steps"].push(item.keyPresses);
                        if (item.runTime < charTime[item.fChar1]["fastest"]) {
                            charTime[item.fChar1]["fastest"] = item.runTime;
                        }
                        if (item.keyPresses < charTime[item.fChar1]["least"]) {
                            charTime[item.fChar1]["least"] = item.keyPresses
                        }
                    } else {
                        charTime[item.fChar1] = {};
                        charTime[item.fChar1]["avgTime"] = 0;
                        charTime[item.fChar1]["avgSteps"] = 0;
                        charTime[item.fChar1]["fastest"] = item.runTime;
                        charTime[item.fChar1]["least"] = item.keyPresses;
                        charTime[item.fChar1]["steps"] = [];
                        charTime[item.fChar1]["steps"].push(item.keyPresses);
                        charTime[item.fChar1]["times"] = [];
                        charTime[item.fChar1]["times"].push(item.runTime);

                    }
                } else {
                    if ($.inArray(item.fChar1, $.map(charDeaths, function (element, index) { return index })) >= 0) {
                        charDeaths[item.fChar1] += 1;
                    } else {
                        charDeaths[item.fChar1] = 1;
                    }
                }
            });
            console.log(totalRuns, totalWins, totalRuns - totalWins, totalTime, totalWinTime, charWins, charDeaths, charTime);
            $.each(charTime, function (i, char) {
                cTime = 0;
                cSteps = 0;
                cLen = char["times"].length
                cLenS = char["steps"].length
                $.each(char["times"], function (j, time) {
                    cTime += time
                });
                $.each(char["steps"], function(j, steps) {
                    cSteps += steps;
                });
                charTime[i]["avgTime"] = cTime / cLen
                charTime[i]["avgSteps"] = cSteps / cLenS
            });
            console.log(charTime);
            output = `<table class="table table-striped table-bordered table-sm table-responsibe-sm table-hover">`;
            output += `<thead>`;
            output += `<tr>`;
            output += `<th scope="col">Char</th>`;
            output += `<th scope="col">Total Wins</th>`
            output += `<th scope="col">Avg Win Time</th>`;
            output += `<th scope="col">Fastest Win Time</th>`;
            output += `<th scope="col">Avg Win Key Presses</th>`;
            output += `<th scope="col">Least Win Key Presses</th>`;
            output += `</tr>`;
            output += `</thead>`;
            output += `<tbody>`;
            $.each(charTime, function(i, char) {
                output += `<tr>`;
                output += `<td>` + i + `</td>`;
                output += `<td>` + char["times"].length + `</td>`;
                output += `<td>` + formatTime(char["avgTime"]) + `</td>`;
                output += `<td>` + formatTime(char["fastest"]) + `</td>`;
                output += `<td>` + Math.trunc(char["avgSteps"]) + `</td>`;
                output += `<td>` + Math.trunc(char["least"]) + `</td>`;
                output += `</tr>`;
            });
            output += `</tbody>`;
            output += `</table>`;
            console.log(output);
            $("#tableStats").html(output);


        });

});

function formatTime(t) {
    millis = Math.trunc(((t/1000) % 1)*100)
    seconds = Math.floor((t/1000) % 60)
    minutes = Math.floor((t/(1000*60)) % 60)
    hours = Math.floor((t/(1000*60*60)) % 24)

    return pad(hours, 2) + ":" + pad(minutes, 2) + ":" + pad(seconds, 2) + "." + pad(millis, 2);
};

function pad(n, width, z) {
    z = z || '0';
    n = n + '';
    return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
  }