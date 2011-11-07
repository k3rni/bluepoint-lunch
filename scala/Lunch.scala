import java.net.URL
import java.util.Scanner
//import scala.util.matching.Regex
import java.util.regex.Pattern
import java.io._
import xml._

class MenuItem(var nazwa: String, var cena:String) {
  override def toString = {
    "MenuItem(%s, %s)".format(nazwa, cena)
  }
}

class Section(var nazwa:String, var cena:String, var items: List[MenuItem]) {
  override def toString = {
    "Section(%s, %s, %s)".format(nazwa, cena, items)
  }

  def this(nazwa:String, cena:String) = this(nazwa, cena, List[MenuItem]())
  def append(t:MenuItem) { items =  t :: items }
}

class LunchMenu {
  var zestawy = List[Section]()
  val zupy = new Section("zupy", "")
  val inne = new Section("inne", "")
  val data:String = "????-??-??"

  override def toString = {
    "LunchMenu(data=%s, zestawy=%s, zupy=%s, inne=%s".format(data, zestawy, zupy, inne)
  }

  def dodajZestaw(zestaw:Section) {
    zestawy = (zestaw :: zestawy.reverse).reverse
  }
}
object Lunch {
  def main(args: Array[String]) {
    val lunch = format_lunch(organize_lunch(parse_lunch(fetch_lunch)))
    println(lunch toString)
  }

  def fetch_lunch():String = {
    val url = new URL("http://4smaki.pl/lunch.xml")
    //XML.load(url) // thx scala za skrót, w dżawie bym się narobił
    // ale i tak nie wystarczy bo to ma zwaloną deklarację  kodowania
    // oneliner do wczytania streama do stringa ze stackoverflow
    val text:String = new Scanner(url.openStream).useDelimiter("\\A").next
    text
  }

  def parse_lunch(text:String):List[Option[MenuItem]] = {
    val lunch = XML.loadString(text.replace("iso-8859-1", "utf-8"))
    lunch.descendant.map { node => 
      node match  {
        case <item></item> =>  { // xml pattern matching, ale tylko struktura
          // przekodowanie
          val cena = node.attribute("cena").head.toString.trim
          val nazwa = node.attribute("nazwa").head.toString.trim
          //println("c:%s n:%s".format(cena, nazwa))
          if (nazwa != "")
            new Some(new MenuItem(nazwa, cena))
          else
            None
        }
        case _ => { None }
      }
    }.filterNot { _ == None }
    //"Not Implemented"
  }

  def organize_lunch(items:List[Option[MenuItem]]):LunchMenu = {
    val menu = new LunchMenu
    var z = menu.inne
    var headers_count = 0
    items.foreach { i1 =>
      val item = i1.get
      if (all_upcase(item.nazwa)) {
        headers_count += 1
        if (headers_count > 1) {
          z = new Section(item.nazwa, item.cena)
          menu.dodajZestaw(z)
        } else {
          // poszukaj daty w nagłówku i sparsuj
        }
      } else if (item.nazwa startsWith "*") {
        if (headers_count == 1)
          menu.zupy append item
        else
          menu.inne append item
      } else
         z append item
      ()
    }
    menu
  }

  def format_lunch(input:LunchMenu) = {
    input
  }

  def all_upcase(text:String) = {
    //Pattern.matches("[\\p{Upper}\\p{Space}\\p{Punct}\\p{Digit}]+", text) // słabe, tylko ascii
    Pattern.matches("^[\\p{Lu}\\p{Zs}\\p{Po}\\p{Pd}\\p{Nd}]+$", text)

    //!(new Regex("^[\\p{Upper}\\p{Space}\\p{Punct}\\p{Digit}]+$") findFirstIn text isEmpty)
  }

}
