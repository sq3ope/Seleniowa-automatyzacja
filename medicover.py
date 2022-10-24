#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: sw=3 sts=3

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

import sys, time, os, datetime, re, locale

from ustawienia import slownik
from ustawienia import konta
import hasla
from scraper import *

class ScraperMedicover(ScraperLekarzy):
  def __init__(self, parametry):
    ScraperLekarzy.__init__(self, adresStartowy="https://mol.medicover.pl",
                                  naglowekWMejlu="MEDICOVER", parametryWejsciowe=parametry)
  def odwiedzIZbierzWyniki(self, sel):
    dzien = 864000000000

    sel.find_element_by_id('oidc-submit').click()
    time.sleep(2)
    glowneOkno = sel.window_handles[0]
    sel.switch_to_window(sel.window_handles[1])
    self.czekajAzSiePojawi(sel, (By.ID, 'UserName'))
    sel.find_element_by_id('UserName').send_keys(slownik['login'])
    sel.find_element_by_id('Password').send_keys(hasla.haslo('medicover', slownik['login'], slownik.get('haslo')))
    time.sleep(2)
    sel.find_element_by_id('Password').send_keys(Keys.RETURN)
    time.sleep(3)
    sel.switch_to_window(glowneOkno)
    
    # ============ po logowaniu

    print "Login successful :)"

    self.czekajAzSiePojawi(sel, (By.ID, "myCarousel"))
    sel.get("https://mol.medicover.pl/MyVisits")
    sel.get("https://mol.medicover.pl/MyVisits?bookingTypeId=2&specializationId=83&selectedSpecialties=83&pfm=1")

    self.czekajAzSiePojawi(sel, (By.XPATH, "//button[text()='Szukaj']"))
    print "Find button found, clicking..."
    
#     time.sleep(2)
#
#     Select(sel.find_element_by_id('RegionId')).select_by_value('204')	# 204 = Warszawa # 207 - Poznan
#
#     self.czekajAzSiePojawi(sel, (By.ID, "SpecializationId"))
#     time.sleep(2)
#
#     print "Szukam %s" % self.specjalizacja
#     spec = Select(sel.find_element_by_id('SpecializationId'))
#     for option in spec.options:
#        if re.findall(self.specjalizacja, option.text):
#           spec.select_by_value(option.get_attribute('value'))
#           break
#

    time.sleep(6)

    sel.find_element_by_xpath("//button[text()='Szukaj']").click()

    element = self.czekajAzSiePojawi(sel, (By.CSS_SELECTOR, '.visitListDate, #phoneImg'))
    if (element.get_attribute("id") == "phoneImg"):
      print "No visits found."
      return []

    print "Got some visits"

    time.sleep(3)

    for i in range(5):
      if not self.czekajAzSiePojawiOpcjonalnie(sel, (By.XPATH, "//button[contains(text(),'Poka')]")):
       print "Next button not found"
       break

      try:
       print "Clicking next button"
       sel.find_element_by_xpath("//button[contains(text(),'Poka')]").click()
      except Exception as e:
       print "Failed to next button: %s" % e
      time.sleep(3)


    days = sel.find_elements_by_css_selector('app-visit-list > div:not(.row)')
    
    wyniki=[]
    
    for day in days:
      date_element = day.find_element_by_css_selector('.visitListDate')
      date_string = date_element.text.encode('utf-8')
      print "Found visit day: %s" % date_string

      #'17 Listopada 2022, Czwartek'
      locale.setlocale(locale.LC_ALL, 'pl_PL')
      date_value = datetime.datetime.strptime(date_string.split(',')[0], '%d %B %Y')

      dane = [date_value]
      for element in day.find_elements_by_css_selector('.slot-time,.specialization,.doctorName,.clinicName'):
        dane.append(element.text)
#       dane = [element.text ]
#       dane[0] = datetime.datetime.strptime(dane[0], "%d/%m/%Y")

#      if (not self.przed) or (dane[0] < self.przed):
      wyniki.append(dane)
    return wyniki


if __name__ == "__main__":
  ScraperMedicover(sys.argv).scrapuj()
  

