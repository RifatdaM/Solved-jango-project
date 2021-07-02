
    var refreshOrderForm1 = function(){
        $.ajax({
            url: "{% url 'get_info_update' %}",
            method: 'GET',
            dataType : "json",
            data: {},
            success: function(response){
              var val = parseFloat(document.getElementById("number1").value);
              if(Number.isNaN(val)){
                val = 0.0;
              }
              madeSelectionfrom = document.getElementById("from_select").value;
              madeSelectionto = document.getElementById("to_select").value;
              var from_val = madeSelectionfrom;
              var to_val = madeSelectionto;
              if(madeSelectionfrom == 'btcusd'){
                from_val = 'bitcoin';
              }

              if(madeSelectionto == 'btcusd'){
                to_val = 'bitcoin';
              }
              document.getElementById("exchange_head").innerHTML = "Buy "+from_val+" with "+to_val;
              document.getElementById("commission_from").innerHTML = from_val;
              document.getElementById("commission_to").innerHTML = to_val;
              var ans = 0;
              var res = 0.0;
              var max = 0.0;
              var rt = 0.0;
              var res_unit = "";
              var from_commi = 0.0;
              var to_commi = 0.0;
              var from_commi_am = 0.0;
              var to_commi_am = 0.0;
              var from_to_to_convert = 0.0;
              var from_unit = "";
              var to_unit = "";
              conversion_rates = response["convert"][0];
              for(var i = 0; i < response["reserves"].length; i++)
              {
                  var product = response["reserves"][i];
                  if(product["title"] == madeSelectionfrom){
                      var rate = parseFloat(product[madeSelectionto]);
                      rt = rate;
                      max = product["maxim"];
                      if(val == 0){ ans = 0; }
                      else{ ans = val*rate; }
                      document.getElementById("from_unit").innerHTML = product["unit"];
                      from_commi = product["from_com"] * 100;
                      from_commi_am = val*product["from_com"];
                      from_commi_am = from_commi_am.toFixed(2);
                      document.getElementById("commission_from_am").innerHTML = from_commi+"%"+" "+from_commi_am+product["unit"];
                      from_unit = product["unit"];
                      var ul = product["title"]+'.png';
                      if(val < product["minim"]){
                        document.getElementById("from_notice").innerHTML = "Select amount more than "+product["minim"]+" "+product["unit"];
                        document.getElementById("buy_button").disabled = true;
                      }
                      else if(val > product["maxim"]){
                        document.getElementById("from_notice").innerHTML = "Select amount less than "+product["maxim"]+" "+product["unit"];
                        document.getElementById("buy_button").disabled = true;
                      }
                      else{
                        document.getElementById("from_notice").innerHTML = "     ";
                        document.getElementById("buy_button").disabled = false;
                      }
                  }
                  if(product["title"] == madeSelectionto){
                      document.getElementById("to_unit").innerHTML = product["unit"];
                      var ul = product["title"]+'.png';
                      res = product["reserve_am"];
                      res_unit = product["unit"];
                      to_unit = product["unit"];
                      to_commi = product["to_com"] * 100;
                  }
              }
              if(ans > res && (rt*max)>res){
                document.getElementById("to_notice").innerHTML = "Select amount less than "+res+" "+res_unit;
                document.getElementById("buy_button").disabled = true;
                document.getElementById("from_notice").innerHTML = "   ";
              }
              else{
                document.getElementById("to_notice").innerHTML = "    ";
              }
              var con_rate = 0.0;
              if(from_unit == 'USD' && to_unit == 'BDT'){
                from_to_to_convert = conversion_rates[madeSelectionfrom];
                con_rate = from_to_to_convert;
              }
              else if(from_unit == 'BDT' && to_unit == 'USD'){
                from_to_to_convert = 1/conversion_rates[madeSelectionto];
                con_rate = from_to_to_convert;
              }
              else{
                from_to_to_convert = 1.00;
                con_rate = 1.00;
              }
              to_commi_am = ((val)*con_rate)*(to_commi/100);
              to_commi_am = to_commi_am.toFixed(2);
              to_commi = to_commi.toFixed(2);
              document.getElementById("commission_to_am").innerHTML = to_commi+"%"+" "+to_commi_am+to_unit;
              var rem = 0.00;
              var exon_commi = 0.00;
              if(from_unit == to_unit && val != 0){
                rem = val - ans - to_commi_am - from_commi_am;
                exon_commi = (rem/val)*100;
              }
              else if(val != 0){
                rem = (val*from_to_to_convert) - ans - to_commi_am - (from_commi_am*from_to_to_convert);
                exon_commi = (rem/(val*from_to_to_convert))*100;
              }
              var un = "USD";

              if(to_unit == 'BDT' && from_unit == 'USD'){
                rem = rem * (1/from_to_to_convert);
                un = "USD";
              }
              else if(to_unit == 'BDT' && from_unit == 'BDT'){
                un = "BDT";
              }
              exon_commi = exon_commi.toFixed(2);
              rem = rem.toFixed(2);
              document.getElementById("commission_exontime_am").innerHTML = exon_commi+"%"+" "+rem+un;
              ans = ans.toFixed(2);
              if(val!=0){
                document.getElementById("number2").value = ans;
              }
            },
            error: function(error){
                console.log(error);
                console.log("error");
            }
        });
    }

    var refreshOrderForm2 = function(){
        $.ajax({
            url: "{% url 'get_info_update' %}",
            method: 'GET',
            dataType : "json",
            data: {},
            success: function(response){
              var val = parseFloat(document.getElementById("number2").value);
              if(Number.isNaN(val)){
                val = 0.0;
              }
              madeSelectionfrom = document.getElementById("from_select").value;
              madeSelectionto = document.getElementById("to_select").value;
              var from_val = madeSelectionfrom;
              var to_val = madeSelectionto;
              if(madeSelectionfrom == 'btcusd'){
                from_val = 'bitcoin';
              }

              if(madeSelectionto == 'btcusd'){
                to_val = 'bitcoin';
              }
              document.getElementById("exchange_head").innerHTML = "Buy "+from_val+" with "+to_val;
              document.getElementById("commission_from").innerHTML = from_val;
              document.getElementById("commission_to").innerHTML = to_val;
              var ans = 0.0;
              var res = 0.0;
              var max = 0.0;
              var rt = 0.0;
              var res_unit = "";
              var from_commi = 0.0;
              var to_commi = 0.0;
              var from_commi_am = 0.0;
              var to_commi_am = 0.0;
              var from_to_to_convert = 0.0;
              var from_unit = "";
              var to_unit = "";
              var res_unit = "";
              conversion_rates = response["convert"][0];
              for(var i = 0; i < response["reserves"].length; i++)
              {
                  var product = response["reserves"][i];
                  if(product["title"] == madeSelectionfrom){
                      var rate = parseFloat(product[madeSelectionto]);
                      rt = rate;
                      if(val == 0){ ans = 0; }
                      else{ ans = val*(1/rate); }
                      document.getElementById("from_unit").innerHTML = product["unit"];
                      from_commi = product["from_com"] * 100;
                      from_commi_am = ans*product["from_com"];
                      from_commi_am = from_commi_am.toFixed(2);
                      document.getElementById("commission_from_am").innerHTML = from_commi+"%"+" "+from_commi_am+product["unit"];
                      from_unit = product["unit"];
                      var ul = product["title"]+'.png';
                      max = product["maxim"];
                      if(ans < product["minim"]){
                        document.getElementById("from_notice").innerHTML = "Select amount more than "+product["minim"]+" "+product["unit"];
                        document.getElementById("buy_button").disabled = true;
                      }
                      else if(ans > product["maxim"]){
                        document.getElementById("from_notice").innerHTML = "Select amount less than "+product["maxim"]+" "+product["unit"];
                        document.getElementById("buy_button").disabled = true;
                      }
                      else{
                        document.getElementById("from_notice").innerHTML = "   ";
                        document.getElementById("buy_button").disabled = false;
                      }
                  }
                  if(product["title"] == madeSelectionto){
                      document.getElementById("to_unit").innerHTML = product["unit"];
                      var ul = product["title"]+'.png';
                      res = product["reserve_am"];
                      res_unit = product["unit"];
                      to_unit = product["unit"];
                      to_commi = product["to_com"] * 100;
                  }
              }

              if(val > res && (rt*max)>res){
                document.getElementById("to_notice").innerHTML = "Select amount less than "+res+" "+res_unit;
                document.getElementById("buy_button").disabled = true;
                document.getElementById("from_notice").innerHTML = "   ";
              }
              else{
                document.getElementById("to_notice").innerHTML = "    ";
              }

              var con_rate = 0.0;
              if(from_unit == 'USD' && to_unit == 'BDT'){
                from_to_to_convert = conversion_rates[madeSelectionfrom];
                con_rate = from_to_to_convert;
              }
              else if(from_unit == 'BDT' && to_unit == 'USD'){
                from_to_to_convert = 1/conversion_rates[madeSelectionto];
                con_rate = from_to_to_convert;
              }
              else{
                from_to_to_convert = 1.00;
                con_rate = 1.00;
              }
              to_commi_am = ((ans)*con_rate)*(to_commi/100);
              to_commi_am = to_commi_am.toFixed(2);
              to_commi = to_commi.toFixed(2);
              document.getElementById("commission_to_am").innerHTML = to_commi+"%"+" "+to_commi_am+to_unit;
              var rem = 0.00;
              var exon_commi = 0.00;
              if(from_unit == to_unit && ans != 0){
                rem = ans - val - to_commi_am - from_commi_am;
                exon_commi = (rem/ans)*100;
              }
              else if(ans != 0){
                rem = (ans*from_to_to_convert) - val - to_commi_am - (from_commi_am*from_to_to_convert);
                exon_commi = (rem/(ans*from_to_to_convert))*100;
              }
              var un = "USD";

              if(to_unit == 'BDT' && from_unit == 'USD'){
                rem = rem * (1/from_to_to_convert);
                un = "USD";
              }
              else if(to_unit == 'BDT' && from_unit == 'BDT'){
                un = "BDT";
              }
              exon_commi = exon_commi.toFixed(2);
              rem = rem.toFixed(2);
              document.getElementById("commission_exontime_am").innerHTML = exon_commi+"%"+" "+rem+un;
              ans = ans.toFixed(2);
              if(val != 0){
                document.getElementById("number1").value = ans;
              }
            },
            error: function(error){
                console.log(error);
                console.log("error");
            }
        });
    }
