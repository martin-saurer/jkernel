// J syntax definition for CodeMirror

(function(mod)
{
   if(typeof exports == "object" && typeof module == "object") // CommonJS
   {
      mod(require("../../lib/codemirror"));
   }
   else if(typeof define == "function" && define.amd) // AMD
   {
      define(["../../lib/codemirror"],mod);
   }
   else // Plain browser env
   {
      mod(CodeMirror);
   }
})

(function(CodeMirror)
{
   "use strict";

   CodeMirror.defineMode('J',function(config)
   {

      var c;
      var words = {};

      function define(style,string)
      {
         var split = string.split(' ');
         for(var i=0;i<split.length;i++)
         {
            words[split[i]] = style;
         }
      };

      // Keywords
      define('keyword','for. goto. label. assert. break. continue. if. do. else. end. elseif. return. select. case. fcase. throw. try. while. whilst. catch. catchd. catcht.');

      function tokenBase(stream,state)
      {
         var sol = stream.sol();
         var ch  = stream.next();

         // String
         if(ch==='\'')
         {
            if(stream.skipTo('\''))
            {
               stream.next();
               return'tag';
            }
         }

         // Comment
         if(ch==='N' && stream.eat('B') && stream.eat('.'))
         {
            c = stream.next();
            if(c!='.' && c!=':')
            {
               stream.skipToEnd();
               return'comment';
            }
         }

         // Assignment Operator
         if(ch==='=' && stream.eat(':'))
         {
            c = stream.next();
            if(c==null)
            {
               return'operator';
            }
            if(c!='.' && c!=':')
            {
               stream.backUp(1);
               return 'operator';
            }
         }
 
         // Assignment Operator
         if(ch==='=' && stream.eat('.'))
         {
            c = stream.next();
            if(c==null)
            {
               return 'operator';
            }
            if(c!='.' && c!=':')
            {
               stream.backUp(1);
               return 'operator';
            }
         }
 
         stream.eatWhile(/\w/);
         var cur = stream.current();

         var i = cur.indexOf("_");
         if(-1!=i)
         {
            cur = cur.substr(0,i);
         }
    
         if(stream.eat('.'))
         {
            if(stream.eol())
            {
               cur = cur + '.';
            }
            else
            {
               c = stream.next();
               if(c!='.' && c!=':')
               {
                  cur = cur + '.';
               }
               stream.backUp(1);
            }
         }

         return words.hasOwnProperty(cur) ? words[cur] : null;

      }; // function tokenBase(stream,state)

      function tokenize(stream,state)
      {
         return (state.tokens[0] || tokenBase) (stream, state);
      };

      // Return
      return {
         startState: function() {
            return {tokens:[]};
         },
         token:      function(stream,state) {
            if(stream.eatSpace())
            {
               return null;
            }
            return tokenize(stream,state);
         }
      };

   }); // CodeMirror.defineMode('J',function(config)

   CodeMirror.defineMIME("text/J","J");

}); // (function(CodeMirror)
