using System;
using System.Diagnostics;

class Program
{
    static void Main()
    {

        Console.WriteLine("OWO Listener Client Initialized");
        

        Process.Start("python", "oworat.py");
    }
}