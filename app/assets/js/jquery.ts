// @ts-types="npm:@types/jquery"
import $ from "npm:jquery";

declare global {
    interface Window {
        jQuery: JQueryStatic;
        $: JQueryStatic;
    }
    interface JQuery {
        appendText: (text: string) => JQuery;
    }
}

window.jQuery = $;
window.$ = $;

$.fn.appendText = function(text) {
    return this.each(function () {
        const textNode = document.createTextNode(text);
        $(this).append(textNode);
    });
};


export default $;