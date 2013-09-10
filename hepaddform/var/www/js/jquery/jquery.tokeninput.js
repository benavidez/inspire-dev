/*
 * jQuery Plugin: Tokenizing Autocomplete Text Entry
 * Version 1.6.0
 *
 * Copyright (c) 2009 James Smith (http://loopj.com)
 * Licensed jointly under the GPL and MIT licenses,
 * choose which one suits your project best!
 *
 */

(function($) {
    // Default settings
    var DEFAULT_SETTINGS = {
        // Search settings
        method: "GET",
        queryParam: "q",
        searchDelay: 0, //ebv 300,
        minChars: 1,
        propertyToSearch: "name",
        jsonContainer: null,
        contentType: "json",

        // Prepopulation settings
        prePopulate: null,
        processPrePopulate: false,

        makeSortable: false,         //Cornelia Drag and Drop - Sortable functionality
        allowOK: false,              //Cornelia for Confirming
        allowDialog: false,          //Cornelia for calling Dialogbox
        searchOnEnter: null,         // arwagner: trigger search on focus() event
        shortSearch: 0,              // if we have less than shortSearch chars...
        shortSearchPrefix: null,     // ...prefix the search with shortSearchPrefix
        // Display settings
        hintText: "Type in a search term",
        noResultsText: "No results",
        searchingText: "", //ebv "Searching...",
        deleteText: "&times;",
        okText: "&nbspok&nbsp",
        //Cornelia for Confirming
        dialogText: "&nbspdialog&nbsp",
        //Cornelia for calling Dialogbox
        animateDropdown: true,
        theme: null,
        zindex: 999,
        resultsFormatter: function(item) {
            if (item === undefined) {
                return undefined;
            } else {
                return "<li>" + item[this.propertyToSearch] + "</li>";
            }
        },
        tokenFormatter: function(item) {
            if (item === undefined) {
                return undefined;
            } else {
                return "<li><p>" + item[this.propertyToSearch] + "</p></li>";
            }
        },

        // Tokenization settings
        tokenLimit: null,
        tokenDelimiter: ",",
        preventDuplicates: true,
        tokenValue: "id",

        // Callbacks
        onResult: null,
        onAdd: null,
        onDelete: null,
        onReady: null,
        onMove: null,        //Cornelia for calling drag and drop event
        onOK: null,          //Cornelia for calling ok event
        onDialog: null,      //Cornelia for calling Dialogbox
        onInit: null,        //Cornelia for calling on init
        // Other settings
        idPrefix: "token-input-",

        // Keep track if the input is currently in disabled mode
        disabled: false


    };

    // Default classes to use when theming
    var DEFAULT_CLASSES = {
        tokenList: "token-input-list",
        token: "token-input-token",
        tokenDelete: "token-input-delete-token",
        tokenEdit: "token-input-edit-token",        //Cornelia for editing tokens 
        tokenOK: "token-input-confirm-token",       //Cornelia for confirming tokens 
        tokenDialog: "token-input-dialog-token",    //Cornelia for calling Dialogbox
        selectedToken: "token-input-selected-token",
        highlightedToken: "token-input-highlighted-token",
        dropdown: "token-input-dropdown",
        dropdownItem: "token-input-dropdown-item",
        dropdownItem2: "token-input-dropdown-item2",
        selectedDropdownItem: "token-input-selected-dropdown-item",
        inputToken: "token-input-input-token",
        disabled: "token-input-disabled",
        insertBefore: "token-input-insert-before",  //Cornelia for D&D - Sortable functionality
        insertAfter: "token-input-insert-after"     //Cornelia for D&D - Sortable functionality
    };

    // Input box position "enum"
    var POSITION = {
        BEFORE: 0,
        AFTER: 1,
        END: 2
    };

    // Keys "enum"
    var KEY = {
        BACKSPACE: 8,
        TAB: 9,
        ENTER: 13,
        ESCAPE: 27,
        SPACE: 32,
        PAGE_UP: 33,
        PAGE_DOWN: 34,
        END: 35,
        HOME: 36,
        LEFT: 37,
        UP: 38,
        RIGHT: 39,
        DOWN: 40,
        NUMPAD_ENTER: 108,
        COMMA: 188
    };

    // Additional public (exposed) methods
    var methods = {
        init: function(url_or_data_or_function, options) {
            var settings = $.extend({}, DEFAULT_SETTINGS, options || {});

            return this.each(function() {
                $(this).data("tokenInputObject", new $.TokenList(this, url_or_data_or_function, settings));
            });
        },
        clear: function() {
            this.data("tokenInputObject").clear();
            return this;
        },
        add: function(item) {
            this.data("tokenInputObject").add(item);
            return this;
        },
        remove: function(item) {
            this.data("tokenInputObject").remove(item);
            return this;
        },
        get: function() {
            return this.data("tokenInputObject").getTokens();
        },
        toggleDisabled: function(disable) {
            this.data("tokenInputObject").toggleDisabled(disable);
            return this;
        },
        //added cornelia for faster prefill
        insert: function(item) {
            this.data("tokenInputObject").insert(item);
            return this;
        }
        //added cornelia end
    };

    // Expose the .tokenInput function to jQuery as a plugin
    $.fn.tokenInput = function(method) {
            // Method calling and initialization logic
            if (methods[method]) {
                return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
            } else {
                return methods.init.apply(this, arguments);
            }
        };

    // TokenList class for each input
    $.TokenList = function(input, url_or_data, settings) {
        //
        // Initialization
        //
        //added Cornelia
        if ($.isFunction(settings.onInit)) settings.onInit.call();
        //end Cornelia
        // Configure the data source
        if ($.type(url_or_data) === "string" || $.type(url_or_data) === "function") {
            // Set the url to query against
            settings.url = url_or_data;

            // If the URL is a function, evaluate it here to do our initalization work
            var url = computeURL();

            // Make a smart guess about cross-domain if it wasn't explicitly specified
            if (settings.crossDomain === undefined && typeof url === "string") {
                if (url.indexOf("://") === -1) {
                    settings.crossDomain = false;
                } else {
                    settings.crossDomain = (location.href.split(/\/+/g)[1] !== url.split(/\/+/g)[1]);
                }
            }
        } else if (typeof(url_or_data) === "object") {
            // Set the local data to search through
            settings.local_data = url_or_data;
        }

        // Build class names
        if (settings.classes) {
            // Use custom class names
            settings.classes = $.extend({}, DEFAULT_CLASSES, settings.classes);
        } else if (settings.theme) {
            // Use theme-suffixed default class names
            settings.classes = {};
            $.each(DEFAULT_CLASSES, function(key, value) {
                settings.classes[key] = value + "-" + settings.theme;
            });
        } else {
            settings.classes = DEFAULT_CLASSES;
        }


        // Save the tokens
        var saved_tokens = [];

        // Keep track of the number of tokens in the list
        var token_count = 0;

        // Basic cache to save on db hits
        var cache = new $.TokenList.Cache();

        // Keep track of the timeout, old vals
        var timeout;
        var input_val;

      	// Keep track of mouse being over dropdown
      	var mouseOverDD;

        // Create a new text input an attach keyup events
        var input_box = $("<input type=\"text\"  autocomplete=\"off\">")
        .css({
            outline: "none"
        }).attr("label", settings.idPrefix + input.label)
        //.attr("id", settings.idPrefix + input.id)
        .focusin(function() {
            if (settings.disabled) {
                return false;
            } else if (settings.tokenLimit === null || settings.tokenLimit !== token_count) {
                show_dropdown_hint();
            }
            // aw
            // in case we want to show an initial search even for the
            // empty box
            if (settings.searchOnEnter !== null) {
                input_box.val(settings.searchOnEnter);
                do_search();
            }
        }).focusout(function() {
            if (!mouseOverDD) {
                  hide_dropdown();
                  $(this).val("");
            }

        }).bind("keyup keydown blur update", resize_input).keydown(function(event) {
            var previous_token;
            var next_token;

            switch (event.keyCode) {
            case KEY.LEFT:
            case KEY.RIGHT:
            case KEY.UP:
            case KEY.DOWN:
                if (!$(this).val()) {
                    previous_token = input_token.prev();
                    next_token = input_token.next();

                    if ((previous_token.length && previous_token.get(0) === selected_token) || (next_token.length && next_token.get(0) === selected_token)) {
                        // Check if there is a previous/next token and it is selected
                        if (event.keyCode === KEY.LEFT || event.keyCode === KEY.UP) {
                            deselect_token($(selected_token), POSITION.BEFORE);
                        } else {
                            deselect_token($(selected_token), POSITION.AFTER);
                        }
                    } else if ((event.keyCode === KEY.LEFT || event.keyCode === KEY.UP) && previous_token.length) {
                        // We are moving left, select the previous token if it exists
                        select_token($(previous_token.get(0)));
                    } else if ((event.keyCode === KEY.RIGHT || event.keyCode === KEY.DOWN) && next_token.length) {
                        // We are moving right, select the next token if it exists
                        select_token($(next_token.get(0)));
                    }
                } else {
                    var dropdown_item = null;

                    if (event.keyCode === KEY.DOWN || event.keyCode === KEY.RIGHT) {
                        dropdown_item = $(selected_dropdown_item).next();
                    } else {
                        dropdown_item = $(selected_dropdown_item).prev();
                    }

                    if (dropdown_item.length) {
                        select_dropdown_item(dropdown_item);
                    }
                }
                return false;
                
            case KEY.BACKSPACE:
                previous_token = input_token.prev();

                if (!$(this).val().length) {
                    if (selected_token) {
                        delete_token($(selected_token));
                        hidden_input.change();
                    } else if (previous_token.length) {
                        select_token($(previous_token.get(0)));
                    }

                    return false;
                } else if ($(this).val().length === 1) {
                    hide_dropdown();
                } else {
                    // set a timeout just long enough to let this function finish.
                    setTimeout(function() {
                        do_search();
                    }, 5);
                }
                break;

            case KEY.TAB:
            case KEY.ENTER:
                //added cornelia for author input
                if (selected_dropdown_item) {
                    add_token($(selected_dropdown_item).data("tokeninput"));
                    hidden_input.change();
                    return false;
                }
                break;
            case KEY.NUMPAD_ENTER:
                if (selected_dropdown_item) {
                    add_token($(selected_dropdown_item).data("tokeninput"));
                    hidden_input.change();
                    return false;
                }
                break;
                //case KEY.COMMA:
                //  if(selected_dropdown_item) {
                //    add_token($(selected_dropdown_item).data("tokeninput"));
                //    hidden_input.change();
                //    return false;
                //  }
                //  break;
                //added cornelia for author input end
            case KEY.ESCAPE:
                hide_dropdown();
                return true;

            default:
                if (String.fromCharCode(event.which)) {
                    // set a timeout just long enough to let this function finish.
                    setTimeout(function() {
                        do_search();
                    }, 5);
                }
                break;
            }
        });

        // Keep a reference to the original input box
        var hidden_input = $(input).hide().val("").focus(function() {
            focus_with_timeout(input_box);
        }).blur(function() {
            input_box.blur();
        });

        // Keep a reference to the selected token and dropdown item
        var selected_token = null;
        var selected_token_index = 0;
        var selected_dropdown_item = null;


        // The list to store the token items in
        var token_list = $("<ul />").addClass(settings.classes.tokenList).click(function(event) {
            var li = $(event.target).closest("li");
            if (li && li.get(0) && $.data(li.get(0), "tokeninput")) {
                toggle_select_token(li);
            } else {
                // Deselect selected token
                if (selected_token) {
                    deselect_token($(selected_token), POSITION.END);
                }

                // Focus input box
                focus_with_timeout(input_box);
            }
        })
        //Cornelia for call dialog for editing tokens 
        .dblclick(function(event) {
            //select token, if not yet selected before
            var li = $(event.target).closest("li");
            if (selected_token === null) toggle_select_token(li);
            //call dialog for selected_token
            if ($.isFunction(settings.onDialog)) {
                settings.onDialog.call(hidden_input, $.data(li.get(0), "tokeninput"));
                deselect_token($(selected_token), POSITION.AFTER);
            }
        })
        //Cornelia for call dialog for editing tokens end
        .mouseover(function(event) {
            var li = $(event.target).closest("li");
            if (li && selected_token !== this) {
                li.addClass(settings.classes.highlightedToken);
            }
        }).mouseout(function(event) {
            var li = $(event.target).closest("li");
            if (li && selected_token !== this) {
                li.removeClass(settings.classes.highlightedToken);
            }
        }).insertBefore(hidden_input);

        // The token holding the input box
        var input_token = $("<li />").addClass(settings.classes.inputToken).appendTo(token_list).append(input_box);

        // The list to store the dropdown items in
        var dropdown = $("<div>")
            .addClass(settings.classes.dropdown)
            .appendTo("body")
            .hide()
            .mouseover(function(){
              mouseOverDD = true;
            })
            .mouseout(function(){
              mouseOverDD = false;
            });

        // Magic element to help us resize the text input
        var input_resizer = $("<tester/>").insertAfter(input_box).css({
            position: "absolute",
            top: -9999,
            left: -9999,
            width: "auto",
            fontSize: input_box.css("fontSize"),
            fontFamily: input_box.css("fontFamily"),
            fontWeight: input_box.css("fontWeight"),
            letterSpacing: input_box.css("letterSpacing"),
            whiteSpace: "nowrap"
        });


        // begin for Drag and Drop - Sortable functionality (inserted of Cornelia)
        // True during dragging process    
        var dragging = false;

        // the dragged Token
        var dragToken;

        // the destination Token
        var dragDestination;
        // end for Drag and Drop - Sortable functionality

        // Pre-populate list if items exist
        hidden_input.val("");
        var li_data = settings.prePopulate || hidden_input.data("pre");
        if (settings.processPrePopulate && $.isFunction(settings.onResult)) {
            li_data = settings.onResult.call(hidden_input, li_data);
        }
        if (li_data && li_data.length) {
            $.each(li_data, function(index, value) {
                insert_token(value);
                checkTokenLimit();
            });
        }

        // Check if widget should initialize as disabled
        if (settings.disabled) {
            toggleDisabled(true);
        }

        // Initialization is done
        if ($.isFunction(settings.onReady)) {
            settings.onReady.call();
        }

        //
        // Public functions
        //
        this.clear = function() {
            token_list.children("li").each(function() {
                if ($(this).children("input").length === 0) {
                    delete_token($(this));
                }
            });
        };

        this.add = function(item) {
            add_token(item);

        };

        this.remove = function(item) {
            token_list.children("li").each(function() {
                if ($(this).children("input").length === 0) {
                    var currToken = $(this).data("tokeninput");
                    var match = true;
                    for (var prop in item) {
                        if (item[prop] !== currToken[prop]) {
                            match = false;
                            break;
                        }
                    }
                    if (match) {
                        delete_token($(this));
                    }
                }
            });
        };

        this.getTokens = function() {
            return saved_tokens;
        };

        this.toggleDisabled = function(disable) {
            toggleDisabled(disable);
        };

        //added Cornelia for faster prefill
        this.insert = function(item) {
            insert_token(item);
        };
        //added Cornelia end

        //
        // Private functions
        //
        // Toggles the widget between enabled and disabled state, or according
        // to the [disable] parameter.


        function toggleDisabled(disable) {
            if (typeof disable === 'boolean') {
                settings.disabled = disable;
            } else {
                settings.disabled = !settings.disabled;
            }
            input_box.prop('disabled', settings.disabled);
            token_list.toggleClass(settings.classes.disabled, settings.disabled);
            // if there is any token selected we deselect it
            if (selected_token) {
                deselect_token($(selected_token), POSITION.END);
            }
            hidden_input.prop('disabled', settings.disabled);
        }

        function checkTokenLimit() {
            if (settings.tokenLimit !== null && token_count >= settings.tokenLimit) {
                input_box.hide();
                hide_dropdown();
                return;
            }
        }

        function resize_input() {
            if (input_val === (input_val = input_box.val())) {
                return;
            }

            // Enter new content into resizer and resize input accordingly
            var escaped = input_val.replace(/&/g, '&amp;').replace(/\s/g, ' ').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            input_resizer.html(escaped);
            input_box.width(input_resizer.width() + 30);
        }

        function is_printable_character(keycode) {
            return ((keycode >= 48 && keycode <= 90) || // 0-1a-z
            (keycode >= 96 && keycode <= 111) || // numpad 0-9 + - / * .
            (keycode >= 186 && keycode <= 192) || // ; = , - . / ^
            (keycode >= 219 && keycode <= 222)); // ( \ ) '
        }

        // Inner function to a token to the list
        // var itemField=[];

        function insert_token(item) {

            var this_token = settings.tokenFormatter(item);

            this_token = $(this_token).addClass(settings.classes.token).insertBefore(input_token);

            // begin for Drag and Drop - Sortable functionality (inserted of Cornelia)
            if (settings.makeSortable) {
                addDragFunctionality(this_token);
            }
            // end for Drag and Drop - Sortable functionality
            // The 'delete token' button
            $("<span>" + settings.deleteText + "</span>").addClass(settings.classes.tokenDelete).appendTo(this_token).click(function() {
                if (!settings.disabled) {
                    delete_token($(this).parent());
                    hidden_input.change();
                    return false;
                }
            });


            // Cornelia for calling a dialog for a token 
            // The 'dialog' button
            if (settings.allowDialog) {
                $("<span>" + settings.dialogText + "</span>").addClass(settings.classes.tokenEdit).appendTo(this_token).click(function() {
                    if ($.isFunction(settings.onDialog)) {
                        settings.onDialog.call(hidden_input, item);
                        deselect_token(this_token, POSITION.AFTER);
                    }
                });
            }
            // Cornelia for calling dialog for token end
            // Cornelia for confirm tokens 
            // The 'ok token' button
            if (settings.allowOK) {
                //control via style color
                //var formated_item = settings.tokenFormatter(item);
                //var style = $(formated_item).attr('style');
                //if (style.search(/red/ig)>=0){
                //or also possible via item attribute 'pasted'
                if (item.pasted) {
                    $("<span>" + settings.okText + "</span>").addClass(settings.classes.tokenOK).appendTo(this_token).click(function() {
                        if ($.isFunction(settings.onOK)) {
                            settings.onOK.call(hidden_input, item);
                            input_token.insertAfter(this_token);
                            insert_token($.data(this_token.get(0), "tokeninput"));
                            this_token.remove();
                        }
                    });
                }
            }
            // Cornelia for confirm tokens end
            //added Cornelia for postion after editing at the end of the tokenlist
            deselect_token(this_token, POSITION.END);
            //added Cornelia end
            // Store data on the token
            if (item !== undefined) {
               var token_data = item;
               $.data(this_token.get(0), "tokeninput", item);

               // Save this token for duplicate checking
               saved_tokens = saved_tokens.slice(0, selected_token_index).concat([token_data]).concat(saved_tokens.slice(selected_token_index));
               selected_token_index++;

               // Update the hidden input
               update_hidden_input(saved_tokens, hidden_input);

               token_count += 1;

               // Check the token limit
               if (settings.tokenLimit !== null && token_count >= settings.tokenLimit) {
                   input_box.hide();
                   hide_dropdown();
               }

               return this_token;
            }
        }

        // Add a token to the token list based on user input


        function add_token(item) {
            var callback = settings.onAdd;


            // See if the token already exists and select it if we don't want duplicates
            if (token_count > 0 && settings.preventDuplicates) {
                var found_existing_token = null;
                token_list.children().each(function() {
                    var existing_token = $(this);
                    var existing_data = $.data(existing_token.get(0), "tokeninput");
                    // change id to label if(existing_data && existing_data.id === item.id) {
                    if (existing_data && existing_data.label === item.label) {
                        found_existing_token = existing_token;
                        return false;
                    }
                });

                if (found_existing_token) {
                    select_token(found_existing_token);
                    input_token.insertAfter(found_existing_token);
                    focus_with_timeout(input_box);
                    return;
                }
            }

            // Insert the new tokens
            if (settings.tokenLimit === null || token_count < settings.tokenLimit) {
                insert_token(item);
                checkTokenLimit();
            }

            // Clear input box
            input_box.val("");

            // Don't show the help dropdown, they've got the idea
            hide_dropdown();

            //Cornelia for reorganise sorting tokens 
            reindex_results();
            //Cornelia end		
            // Execute the onAdd callback if defined
            if ($.isFunction(callback)) {
                callback.call(hidden_input, item);
            }

        }

        // begin Drag and Drop - Sortable functionality (inserted of Cornelia)


        function addDragFunctionality(token) {

            token.bind('mousedown', function() {
                var token = $(this);
                dragToken = token;
                token.addClass(settings.classes.selectedToken);
                dragging = true;
                $(document).one('mouseup', function() {
                    token.removeClass(settings.classes.selectedToken);
                    dragging = false;
                    move_token(token, dragDestination);
                    reindex_results();
                    //add Cornelia for right position of this afer moving 
                    dragDestination = $(this);
                    //add Cornelia for calling drag and drop event for adjusting hidden output
                    if ($.isFunction(settings.onMove)) {
                        settings.onMove.call(hidden_input, $.data(token.get(0), "tokeninput"));
                    }
                    //end Cornelia
                });
                return false;
            }).bind('mouseover', function() {
                if (!dragging) return;
                dragDestination = $(this);
                if (is_after(dragToken, dragDestination)) {
                    dragDestination.addClass(settings.classes.insertAfter);
                } else {
                    dragDestination.addClass(settings.classes.insertBefore);
                }
            }).bind('mouseout', function() {
                if (!dragging) return;
                $(this).removeClass(settings.classes.insertBefore);
                $(this).removeClass(settings.classes.insertAfter);
            }).bind('mouseup', function() {
                $(this).removeClass(settings.classes.insertBefore);
                $(this).removeClass(settings.classes.insertAfter);
            });
        }


        function move_token(token, destinationToken) {

            if (destinationToken === undefined) return; //added Cornelia otherwise error 'destinationToken is undefined'
            if (token.get(0) == destinationToken.get(0)) return;

            if (is_after(token, destinationToken)) {
                token.insertAfter(destinationToken);
            } else {
                token.insertBefore(destinationToken);
            }

        }

        function is_after(first, last) {
            index_tokens();
            first = $.data(first.get(0), "tokeninput");
            last = $.data(last.get(0), "tokeninput");
            if (last === undefined) last = 0; //added Cornelia otherwise error 'last is undefined'	
            return last.index > first.index;
        }


        function index_tokens() {
            var i = 0;
            token_list.find('li').each(function() {
                var data = $.data(this, "tokeninput");
                if (data) {
                    data.index = i;
                }
                i++;
            });
        }

        function reindex_results() {
            var ids = [],
                tokens = [];
            token_list.find('li').each(function() {
                var data = $.data(this, "tokeninput");
                if (data) {
                    ids.push(data.id);
                    tokens.push(data);
                }
            });
            saved_tokens = tokens;
            hidden_input.val(ids.join(settings.tokenDelimiter));

            // added Cornelia for (total) update hidden input (for correct html for mandatory checks)
            update_hidden_input(saved_tokens, hidden_input);
            // added Cornelia end
        }
        // end Drag and Drop - Sortable functionality 

        // Select a token in the token list


        function select_token(token) {
            if (!settings.disabled) {
                token.addClass(settings.classes.selectedToken);
                selected_token = token.get(0);

                // Hide input box
                input_box.val("");

                // Hide dropdown if it is visible (eg if we clicked to select token)
                hide_dropdown();
            }

        }

        // Deselect a token in the token list


        function deselect_token(token, position) {
            token.removeClass(settings.classes.selectedToken);
            selected_token = null;

            if (position === POSITION.BEFORE) {
                input_token.insertBefore(token);
                selected_token_index--;
            } else if (position === POSITION.AFTER) {
                input_token.insertAfter(token);
                selected_token_index++;
            } else {
                input_token.appendTo(token_list);
                selected_token_index = token_count;
            }

            // Show the input box and give it focus again
            focus_with_timeout(input_box);

        }

        // Toggle selection of a token in the token list


        function toggle_select_token(token) {
            var previous_selected_token = selected_token;

            if (selected_token) {
                deselect_token($(selected_token), POSITION.END);
            }

            if (previous_selected_token === token.get(0)) {
                deselect_token(token, POSITION.END);
            } else {
                select_token(token);
            }
        }

        // Delete a token from the token list


        function delete_token(token) {
            // Remove the id from the saved list
            var token_data = $.data(token.get(0), "tokeninput");
            var callback = settings.onDelete;

            var index = token.prevAll().length;
            if (index > selected_token_index) index--;

            // Delete the token
            token.remove();
            selected_token = null;

            // Show the input box and give it focus again
            focus_with_timeout(input_box);

            // Remove this token from the saved list
            saved_tokens = saved_tokens.slice(0, index).concat(saved_tokens.slice(index + 1));
            if (index < selected_token_index) selected_token_index--;

            // Update the hidden input
            update_hidden_input(saved_tokens, hidden_input);

            token_count -= 1;

            if (settings.tokenLimit !== null) {
                input_box.show().val("");
                focus_with_timeout(input_box);
            }

            // Execute the onDelete callback if defined
            if ($.isFunction(callback)) {
                callback.call(hidden_input, token_data);
            }
        }

        // Update the hidden input box value


        function update_hidden_input(saved_tokens, hidden_input) {
            var token_values = $.map(saved_tokens, function(el) {
                if (typeof settings.tokenValue == 'function') return settings.tokenValue.call(this, el);

                return el[settings.tokenValue];
            });
            hidden_input.val(token_values.join(settings.tokenDelimiter));

        }

        // Hide and clear the results dropdown


        function hide_dropdown() {
            dropdown.hide().empty();
            selected_dropdown_item = null;
        }

        function show_dropdown() {
            dropdown.css({
                position: "absolute",
                top: $(token_list).offset().top + $(token_list).outerHeight(),
                left: $(token_list).offset().left,
                width: $(token_list).outerWidth(),
                'z-index': settings.zindex
            }).show();
        }

        function show_dropdown_searching() {
            if (settings.searchingText) {
                dropdown.html("<p>" + settings.searchingText + "</p>");
                show_dropdown();
            }
        }

        function show_dropdown_hint() {
            if (settings.hintText) {
                dropdown.html("<p>" + settings.hintText + "</p>");
                show_dropdown();
            }
        }

        //Highlight the query part of the search term


        function highlight_term(value, term) {

            return value;
            // disable fancy regexp stuff. arwagner
            // return value.replace(new RegExp("(?![^&;]+;)(?!<[^<>]*)(" + term + ")(?![^<>]*>)(?![^&;]+;)", "gi"), "<b>$1</b>");
        }

        function find_value_and_highlight_term(template, value, term) {
            return template;
            // The original code has problems if value contains
            // characters that are themselves regular expressions e.g.
            // a ? or the like. This causes js to crash and thus
            // disables everything. Better not be fancy but working ;)
            // arwagner
            // Original Code: 
            // return template.replace(new RegExp("(?![^&;]+;)(?!<[^<>]*)(" + value + ")(?![^<>]*>)(?![^&;]+;)", "g"), highlight_term(value, term));
        }

        // Populate the results dropdown with some results


        function populate_dropdown(query, results) {
            if (results && results.length) {
                dropdown.empty();
                var dropdown_ul = $("<ul>").appendTo(dropdown).mouseover(function(event) {
                    select_dropdown_item($(event.target).closest("li"));
                }).mousedown(function(event) {
                    add_token($(event.target).closest("li").data("tokeninput"));
                    hidden_input.change();
                    return false;
                }).hide();

                $.each(results, function(index, value) {
                    var this_li = settings.resultsFormatter(value);

                    this_li = find_value_and_highlight_term(this_li, value[settings.propertyToSearch], query);

                    this_li = $(this_li).appendTo(dropdown_ul);

                    if (index % 2) {
                        this_li.addClass(settings.classes.dropdownItem);
                    } else {
                        this_li.addClass(settings.classes.dropdownItem2);
                    }

                    if (index === 0) {
                        select_dropdown_item(this_li);
                    }

                    $.data(this_li.get(0), "tokeninput", value);
                });

                show_dropdown();

                if (settings.animateDropdown) {
                    dropdown_ul.slideDown("fast");
                } else {
                    dropdown_ul.show();
                }
            } else {
                if (settings.noResultsText) {
                    dropdown.html("<p>" + settings.noResultsText + "</p>");
                    show_dropdown();
                }
            }
        }

        // Highlight an item in the results dropdown


        function select_dropdown_item(item) {
            if (item) {
                if (selected_dropdown_item) {
                    deselect_dropdown_item($(selected_dropdown_item));
                }

                item.addClass(settings.classes.selectedDropdownItem);
                selected_dropdown_item = item.get(0);
            }
        }

        // Remove highlighting from an item in the results dropdown


        function deselect_dropdown_item(item) {
            item.removeClass(settings.classes.selectedDropdownItem);
            selected_dropdown_item = null;
        }

        // Do a search and show the "searching" dropdown if the input is longer
        // than settings.minChars


        function do_search() {

            var query = input_box.val();

            // if the input_box.val() is at max settings.shortSearch long,
            // prefix it with shortSearchPrefix and set the query
            // accordingsly. This ensures that we are searching with the
            // prefix and all caching is done properly.
            if (query.length) {
                pos = query.indexOf(settings.shortSearchPrefix);
                if (query.length <= settings.shortSearch) {
                    if (pos !== 0) {
                        input_box.val(settings.shortSearchPrefix + query);
                    }
                } else {
                    if (pos === 0) {
                        input_box.val(query.substr(pos + settings.shortSearchPrefix.length));
                    }
                }
            }
            query = input_box.val();

            if (query && query.length) {

                if (selected_token) {
                    deselect_token($(selected_token), POSITION.AFTER);
                }

                if (query.length >= settings.minChars) {
                    show_dropdown_searching();
                    clearTimeout(timeout);

                    timeout = setTimeout(function() {
                        run_search(query);
                    }, settings.searchDelay);
                } else {
                    hide_dropdown();
                }
            }

        }

        // Do the actual search


        function run_search(query) {
            var cache_key = query + computeURL();
            var cached_results = cache.get(cache_key);
            if (cached_results) {
                populate_dropdown(query, cached_results);
            } else {
                // Are we doing an ajax search or local data search?
                if (settings.url) {
                    var url = computeURL();
                    // Extract exisiting get params
                    var ajax_params = {};
                    ajax_params.data = {};
                    if (url.indexOf("?") > -1) {
                        var parts = url.split("?");
                        ajax_params.url = parts[0];

                        var param_array = parts[1].split("&");
                        $.each(param_array, function(index, value) {
                            var kv = value.split("=");
                            ajax_params.data[kv[0]] = kv[1];
                        });
                    } else {
                        ajax_params.url = url;
                    }

                    // Prepare the request
                    ajax_params.data[settings.queryParam] = query;
                    ajax_params.type = settings.method;
                    ajax_params.dataType = settings.contentType;
                    if (settings.crossDomain) {
                        ajax_params.dataType = "jsonp";
                    }


                    //arwagner: add a datafilter function to form proper JSON
                    //from a text string
                    ajax_params.dataFilter = function(text, type) {
                        text = WashJSstr(text);
                        if (text.indexOf('[') == 0) {
                          obj = JSON.parse(text);
                        }
                        else {
                          text = '[' + text + ']';
                          obj = JSON.parse(text);
                        }
                        obj = JSON.stringify(obj);
                        return obj;
                    };

                    // Attach the success callback
                    ajax_params.success = function(results) {
                        if ($.isFunction(settings.onResult)) {
                            results = settings.onResult.call(hidden_input, results);
                        }
                        cache.add(cache_key, settings.jsonContainer ? results[settings.jsonContainer] : results);

                        // only populate the dropdown if the results are associated with the active search query
                        if (input_box.val() === query) {
                            populate_dropdown(query, settings.jsonContainer ? results[settings.jsonContainer] : results);
                        }
                    };

                    // Make the request
                    $.ajax(ajax_params);
                } else if (settings.local_data) {
                    // Do the search through local data
                    var results = $.grep(settings.local_data, function(row) {
                        return row[settings.propertyToSearch].toLowerCase().indexOf(query.toLowerCase()) > -1;
                    });

                    if ($.isFunction(settings.onResult)) {
                        results = settings.onResult.call(hidden_input, results);
                    }
                    cache.add(cache_key, results);
                    populate_dropdown(query, results);
                }
            }
        }


        // compute the dynamic URL


        function computeURL() {
            var url = settings.url;
            if (typeof settings.url == 'function') {
                url = settings.url.call(settings);
            }
            return url;
        }

        // Bring browser focus to the specified object.
        // Use of setTimeout is to get around an IE bug.
        // (See, e.g., http://stackoverflow.com/questions/2600186/focus-doesnt-work-in-ie)
        // 
        // obj: a jQuery object to focus()


        function focus_with_timeout(obj) {
            setTimeout(function() {
                obj.focus();
            }, 50);
        }

    };

    // Really basic cache for the results
    $.TokenList.Cache = function(options) {
        var settings = $.extend({
            max_size: 500
        }, options);

        var data = {};
        var size = 0;

        var flush = function() {
                data = {};
                size = 0;
            };

        this.add = function(query, results) {
            if (size > settings.max_size) {
                flush();
            }

            if (!data[query]) {
                size += 1;
            }

            data[query] = results;
        };

        this.get = function(query) {
            return data[query];
        };
    };
}(jQuery));
