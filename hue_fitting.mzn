set of float: available_hue;
int: nHues;
array[1..nHues] of var available_hue: hues;
include "increasing.mzn";
constraint increasing(hues);
var float: obj = min(
  [hues[i+1] - hues[i] | i in 1..nHues-1] ++  
  [hues[nHues] - hues[1]] ++ 
  [360.0 - hues[i+1] + hues[i] | i in 1..nHues-1] ++  
  [360.0 - hues[nHues] + hues[1]]
);
solve maximize obj;