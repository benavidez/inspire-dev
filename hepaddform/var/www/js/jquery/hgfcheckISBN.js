function checkISBNvalisate(){

  var isbn=$("#I020__a").val();

  if (typeof isbn === 'undefined') { return true }
  
  if(isbn.match(/[^0-9xX\.\-\s]/)) {
    alert("ISBN darf nur arabische Ziffern und an der letzten Stelle ein X entahlten");
    
	return false;
	
  }
 
  isbn = isbn.replace(/[^0-9xX]/g);
 
  if(isbn.length != 10 && isbn.length != 13) {
    alert("ISBN ist eine 10-stellige oder 13-stellige Id-Nr.");
    return false;
  } else{
	  // alert("richtige ISBN Angabe");
    return true;	
	}
     
	 
  
}
