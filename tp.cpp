// exemple de code test a compiler pour verifier que tout est ok
#include "color.h"
#include "image.h"
#include "image_io.h"
#include "vec.h"
#include <limits>
#include <cmath>
#include <algorithm>
#include <random>
#include <chrono>
const float inf= std::numeric_limits<float>::infinity();

struct Plan {
    Point a;
    Vector n;
    Color color;
};

struct Sphere {
    Point c;
    float r;
    Color color;
};

struct Objet {
    int id; // 0 pour plan, 1 pour sphere
    Plan* p;
    Sphere* s;
};

struct Hit {
    float t;
    Vector n;
    Color color;
    operator bool() const { return (t < inf && t > 0); }
};

struct Source {
    Point o;
    Color color;
};

struct Position {
    Point o;
    Vector d;
};

struct Scene {
    Objet objets[3];  //! remplacer par vector<Objet> objets;
    int nb_objets;
};

Hit intersect_plan( /* parametres du plan */ const Plan& plan, /* parametres de la camera */ const Position& position)
{
    float intersect = dot(plan.n, Vector(position.o ,plan.a)) / dot(plan.n, position.d);
    if (intersect < 0) {
        return {inf, plan.n, plan.color};
    }
    return {intersect, plan.n, plan.color};

}

Vector calcul_normale_sphere(/*intersection */ float intersection, const Sphere& sphere, /* parametres de la camera */ const Position& position)
{
    //Point d'intersection
    Point p = Point(position.o.x + position.d.x * intersection, position.o.y + position.d.y * intersection, position.o.z + position.d.z * intersection);
    //Vecteur normal
    return Vector(sphere.c, p);
}

Hit intersect_sphere( /* parametres de la sphere */ const Sphere& sphere, /* parametres de la camera */ const Position& position)
{
    float a= dot(position.d, position.d);
    float b= dot(2* position.d, Vector(sphere.c, position.o));
    float k= dot(Vector(sphere.c, position.o), Vector(sphere.c, position.o)) - sphere.r*sphere.r;
    float det= b*b - 4*a*k;

    if(det < 0) {
        return {inf, Vector(Point(0,0,0), Point(0,0,0)) , sphere.color};
    } else {
        float t1= (-b + sqrt(det)) / (2*a);
        float t2= (-b - sqrt(det)) / (2*a);
        if(t1 < 0 && t2 < 0) return {inf, Vector(Point(0,0,0), Point(0,0,0)), sphere.color};
        if(t1 < 0) return {t2, calcul_normale_sphere(t2, sphere, position), sphere.color};
        if(t2 < 0) return {t1, calcul_normale_sphere(t1, sphere, position), sphere.color};
        return {std::min(t1, t2), calcul_normale_sphere(std::min(t1, t2), sphere, position), sphere.color};
    }
}

Hit intersect (const Scene& scene, const Position& position) {
    Hit hit = {inf, Vector(Point(0,0,0), Point(0,0,0)), White()};
    for (int i = 0; i < scene.nb_objets; i++) {
        if (scene.objets[i].id == 0) {
            Hit hit_plan = intersect_plan(*scene.objets[i].p, position);
            if (hit_plan.t < hit.t) {
                hit = hit_plan;
            }
        } else {
            Hit hit_sphere = intersect_sphere(*scene.objets[i].s, position);
            if (hit_sphere.t < hit.t) {
                hit = hit_sphere;
            }
        }
    }
    return hit;
}

// Tester intersect_plan
// int main( )
// {
//     // rayon
//     Point o= Point(0, 0, 0);
//     Vector d= Vector(0, 0, -1);

//     // plan
//     Point a= Point(0, 0, -1);
//     Vector n= Vector(0, 0, 1);

//     float t= intersect_plan(a, n, o, d);

//     std::cout << t << std::endl;
//     if(t != 1) std::cout << "oops, loupe\n";
//     else       std::cout << "c'est bon...\n";

//     return 0;
// }

//tester intersect_sphere
// int main( )
// {
//     // rayon
//     Point o= Point(0, 0, 0);
//     Vector d= Vector(0, 0, -1);

//     // sphere
//     Point c= Point(0, 0, 0);
//     float r= 1;

//     float t= intersect_sphere(c, r, o, d);

//     std::cout << t << std::endl;
//     if(t != 1) std::cout << "oops, loupe\n";
//     else       std::cout << "c'est bon...\n";

//     return 0;
// }


//--------------------------------------------------------sans antialiasing--------------------------------------------------------------


void sansAntialiasing()
{
    //creer la scene
    Scene scene;
    scene.nb_objets = 3;
    //camera
    Position camera;
    camera.o = Point(0, 0, 0);
    //Source de lumière
    Source source;
    source.o = Point(1, 3, -1);
    source.color = White() * 10;
    // sphere1
    Point c= Point(0, 0, -5);
    float r= 1;
    Sphere s;
    s.c = c;
    s.r = r;
    s.color = Red();
    Objet o1; 
    o1.id = 1;
    o1.s = &s;
    o1.p = NULL;
    // plan
    Point a= Point(0, -1, 0);
    Vector n= Vector(0, 1, 0);
    Plan p;
    p.a = a;
    p.n = n;
    p.color = Green();
    Objet o2;
    o2.id = 0;
    o2.p = &p;
    o2.s = NULL;
    // sphere2
    Point c2= Point(-2, 0, -2);
    float r2= 1;
    Sphere s2;
    s2.c = c2;
    s2.r = r2;
    s2.color = Blue();
    Objet o3;
    o3.id = 1;
    o3.s = &s2;
    o3.p = NULL;
    //rempli le tableau
    scene.objets[0] = o1;
    scene.objets[1] = o2;
    scene.objets[2] = o3;
    //dimensions images 
    int width = 1024;
    int height = 512;
    int ratioH = width / height;
    int ratioW = height / width; 
    // cree l'image resultat
    Image image(width, height); 
    //crer epsilon
    float epsilon = 0.001;

    for(int py= 0; py < image.height(); py++)
    for(int px= 0; px < image.width(); px++)
    {    
        // extremite
        Point e = Point( (2 * px / (float)image.width()) - 1, (2 * py / (float)image.height()) - 1, -1);
        camera.d= Vector(camera.o, e);     // direction : extremite - origine

        if(ratioH > 1) {
            camera.d.x = camera.d.x * ratioH;
        } else {
            camera.d.y = camera.d.y * ratioW;
        }

        Color color= Black(); 
        Hit infosIntersect = intersect(scene, camera);

        //Point d'intersection
        Point p = Point(camera.o.x + camera.d.x * infosIntersect.t, camera.o.y + camera.d.y * infosIntersect.t, camera.o.z + camera.d.z * infosIntersect.t);

        //Vecteur normal
        Vector normal = infosIntersect.n;

        //Vector lumiere = Vector(p, source.o);
        Position position;
        position.o = p + normal * epsilon;

        //Vecteur lumière
        Vector lumiere = Vector(position.o, source.o);

        position.d = lumiere;

        Hit infosIntersect2 = intersect(scene, position);

        if((infosIntersect2.t < 0) || (infosIntersect2.t > 1))
        {
            float cos_theta= dot(normalize(normal), normalize(lumiere));
            color = source.color * infosIntersect.color * abs(cos_theta) / length2(lumiere);
            color.a = 1;
        } 
        image(px, py)= color;
    }
    write_image(image, "image.png");
}



//--------------------------------------------------------avec antialiasing--------------------------------------------------------------

const int NB_ECHANTILLONS = 300;

void avecAntialiasing()
{
    //creer la scene
    Scene scene;
    scene.nb_objets = 3;
    //camera
    Position camera;
    camera.o = Point(0, 0, 0);
    //Source de lumière
    Source source;
    source.o = Point(1, 3, -1);
    source.color = White() * 10;
    // sphere1
    Point c= Point(0, 0, -5);
    float r= 1;
    Sphere s;
    s.c = c;
    s.r = r;
    s.color = Red();
    Objet o1; 
    o1.id = 1;
    o1.s = &s;
    o1.p = NULL;
    // plan
    Point a= Point(0, -1, 0);
    Vector n= Vector(0, 1, 0);
    Plan p;
    p.a = a;
    p.n = n;
    p.color = Green();
    Objet o2;
    o2.id = 0;
    o2.p = &p;
    o2.s = NULL;
    // sphere2
    Point c2= Point(-2, 0, -2);
    float r2= 1;
    Sphere s2;
    s2.c = c2;
    s2.r = r2;
    s2.color = Blue();
    Objet o3;
    o3.id = 1;
    o3.s = &s2;
    o3.p = NULL;
    //rempli le tableau
    scene.objets[0] = o1;
    scene.objets[1] = o2;
    scene.objets[2] = o3;
    //dimensions images 
    int width = 1024;
    int height = 512;
    int ratioH = width / height;
    int ratioW = height / width; 
    // cree l'image resultat
    Image image(width, height); 
    //crer epsilon
    float epsilon = 0.001;

    #pragma omp parallel for schedule(dynamic, 1)

    for(int py= 0; py < image.height(); py++)
    {
        std::random_device hwseed;
        std::default_random_engine rng( hwseed() );
        std::uniform_real_distribution<float> u;

        for(int px= 0; px < image.width(); px++)
        {    
            Color pixel; 

            for(int pa= 0; pa < NB_ECHANTILLONS; pa++) {

                Color color= Black(); 

                float ux= u(rng); 
                float uy= u(rng);

                //point x y z du plan image
                float x = float(px + ux) / float(image.width()) * 2 - 1;
                float y = float(py + uy) / float(image.height()) * 2 - 1;
                float z = -1;

                Point e = Point(x, y, z);
                camera.d= Vector(camera.o, e);     // direction : extremite - origine

                if(ratioH > 1) {
                    camera.d.x = camera.d.x * ratioH;
                } else {
                    camera.d.y = camera.d.y * ratioW;
                }
    
                Hit infosIntersect = intersect(scene, camera);

                if(infosIntersect){
                    //Point d'intersection
                    Point p = Point(camera.o.x + camera.d.x * infosIntersect.t, camera.o.y + camera.d.y * infosIntersect.t, camera.o.z + camera.d.z * infosIntersect.t);

                    //Vecteur normal
                    Vector normal = infosIntersect.n;

                    //Vector lumiere = Vector(p, source.o);
                    Position position;
                    position.o = p + normal * epsilon;

                    //Vecteur lumière
                    Vector lumiere = Vector(position.o, source.o);

                    position.d = lumiere;

                    Hit infosIntersect2 = intersect(scene, position);

                    if((infosIntersect2.t < 0) || (infosIntersect2.t > 1))
                    {
                        float cos_theta= dot(normalize(normal), normalize(lumiere));
                        color = source.color * infosIntersect.color * abs(cos_theta) / length2(lumiere);
                        color.a = 1;
                        pixel = pixel + color;
                    } 
                }
            }
            pixel.a = 1;
            image(px, py)= Color(pixel / NB_ECHANTILLONS, 1);
        }
    }
    write_image(image, "image.png");
}

int main()
{
    avecAntialiasing();
    return 0;
}