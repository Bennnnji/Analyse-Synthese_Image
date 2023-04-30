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
#include <vector>

const float inf= std::numeric_limits<float>::infinity();

const int NB_ECHANTILLONS = 10;
const float EPSILON = 0.001;

//------------------------------------------------------------ DÉFINITION DES STRUCTURES ------------------------------------------------------------

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

struct Panneau {
    Vector u;
    Vector v;
    Point o;
    Vector n;
    Color color;
};

struct Objet {
    int id; // 0 pour plan, 1 pour sphere, 2 pour panneau
    Plan* p;
    Sphere* s;
    Panneau* panneau;
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

// utilisée pour la caméra et les rayons réfléchis
struct Position {
    Point o;
    Vector d;
};

struct Scene {
    std::vector<Objet> objets;
    int nb_objets;
};

//------------------------------------------------------------ DÉFINITION DES FONCTIONS ------------------------------------------------------------

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

Hit intersect_panneau(const Panneau& panneau, const Position& position) {
    // Calcul de l'intersection avec le plan du panneau
    float intersect = dot(panneau.n, Vector(position.o, panneau.o)) / dot(panneau.n, position.d);
    if (intersect < 0) {
        // L'intersection est derrière la caméra, il n'y a pas de point visible
        return {inf, panneau.n, panneau.color};
    }
    Point p = position.o + intersect * position.d;

    // Vérification que le point d'intersection se trouve dans le panneau
    float norme_u = panneau.u.x * panneau.u.x + panneau.u.y * panneau.u.y + panneau.u.z * panneau.u.z; 
    float norme_v = panneau.v.x * panneau.v.x + panneau.v.y * panneau.v.y + panneau.v.z * panneau.v.z; 

    Vector op = Vector(panneau.o, p);
    float u = dot(op, panneau.u) / (norme_u * norme_u);
    float v = dot(op, panneau.v) / (norme_v * norme_v);
    if (u < 0 || u > 1 || v < 0 || v > 1) {
        // Le point d'intersection est en dehors du panneau, il n'y a pas de point visible
        return {inf, panneau.n, panneau.color};
    }
    // Le point d'intersection est visible, on retourne l'information sur le point d'intersection
    return {intersect, panneau.n, panneau.color};
}

Hit intersect (const Scene& scene, const Position& position) {
    Hit hit = {inf, Vector(Point(0,0,0), Point(0,0,0)), White()};
    for (int i = 0; i < scene.nb_objets; i++) {
        if (scene.objets[i].id == 0) {
            Hit hit_plan = intersect_plan(*scene.objets[i].p, position);
            if (hit_plan.t < hit.t) {
                hit = hit_plan;
            }
        } else if (scene.objets[i].id == 1) {
            Hit hit_sphere = intersect_sphere(*scene.objets[i].s, position);
            if (hit_sphere.t < hit.t) {
                hit = hit_sphere;
            }
        } else if (scene.objets[i].id == 2) {
            Hit hit_panneau = intersect_panneau(*scene.objets[i].panneau, position);
            if (hit_panneau.t < hit.t) {
                hit = hit_panneau;
            }
        }
    }
    return hit;
}

void computePixelColorDome(const std::vector<Vector>& directions, const Scene& scene, Color& pixel, const Hit& infosIntersect, const Position& camera)
{
    //Point d'intersection
    Point p = Point(camera.o.x + camera.d.x * infosIntersect.t, camera.o.y + camera.d.y * infosIntersect.t, camera.o.z + camera.d.z * infosIntersect.t);

    //Vecteur normal
    Vector normal = infosIntersect.n;

    //Vector lumiere = Vector(p, source.o);
    Position position;
    position.o = p + normal * EPSILON;

    //itérer sur les lumières
    for (int i = 0; i < directions.size(); i++)
    {
        Vector direction = directions[i];
        position.d = direction;

        Hit infosIntersect2 = intersect(scene, position);

        if ((infosIntersect2.t < 0) || (infosIntersect2.t > 1))
        {
            float cos_theta = dot(normalize(normal), normalize(direction));
            Color color = White() / directions.size() * infosIntersect.color * abs(cos_theta) / length2(direction);
            color.a = 1;
            pixel = pixel + color;
        }
    }
}

void computePixelColorSources(const std::vector<Source>& sources, const Scene& scene, Color& pixel, Color& color, const Hit& infosIntersect, const Position& camera)
{
    //Point d'intersection
    Point p = Point(camera.o.x + camera.d.x * infosIntersect.t, camera.o.y + camera.d.y * infosIntersect.t, camera.o.z + camera.d.z * infosIntersect.t);

    //Vecteur normal
    Vector normal = infosIntersect.n;

    //Vector lumiere = Vector(p, source.o);
    Position position;
    position.o = p + normal * EPSILON;

    //itérer sur les lumières
    for(int i= 0; i < sources.size() ; i++)
    {
        Source source = sources[i];

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


//--------------------------------------------------------avec antialiasing & sans dome--------------------------------------------------------------

void avecAntialiasingSansDome(Scene scene, Position camera, std::vector<Source> sources, int width, int height)
{
    int ratioH = width / height;
    int ratioW = height / width; 
    // cree l'image resultat
    Image image(width, height); 

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
                    computePixelColorSources(sources, scene, pixel, color, infosIntersect, camera);
                }
            }
            pixel.a = 1;
            image(px, py)= Color(pixel / NB_ECHANTILLONS, 1);
        }
    }
    write_image(image, "image.png");
}

//--------------------------------------------------------avec antialiasing & un dome en source de lumière--------------------------------------------------------------

void avecAntialiasingAvecDome(Scene scene, Position camera, int width, int height)
{
    std::random_device hwseed;
    unsigned seed= hwseed(); 
    std::default_random_engine rng( seed ); 
    std::uniform_real_distribution<float> u;
    std::vector <Vector> directions; 
    for(int i= 0; i < 64; i++)
    {
        float cos_theta= u(rng);
        float sin_theta= std::sqrt(1 - cos_theta*cos_theta);
        float phi= u(rng) * float(M_PI*2);
        Vector d= Vector(std::cos(phi) * sin_theta , cos_theta ,std::sin(phi) * sin_theta); 
        directions.push_back( d );
    }

    int ratioH = width / height;
    int ratioW = height / width; 
    // cree l'image resultat
    Image image(width, height); 

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
                    computePixelColorDome(directions,scene, pixel, infosIntersect, camera);
                } else {
                    pixel = pixel + White();
                }
            }
            pixel.a = 1;
            image(px, py)= Color(pixel / NB_ECHANTILLONS, 1);
        }
    }
    write_image(image, "image.png");
}

//--------------------------------------------------------avec antialiasing & tout (dome + vector de sources) --------------------------------------------------------------

void avecAntialiasingEtAll(Scene scene, Position camera, std::vector<Source> sources, int width, int height)
{
    std::random_device hwseed;
    unsigned seed= hwseed(); 
    std::default_random_engine rng( seed ); 
    std::uniform_real_distribution<float> u;
    std::vector <Vector> directions; 
    for(int i= 0; i < 64; i++)
    {
        float cos_theta= u(rng);
        float sin_theta= std::sqrt(1 - cos_theta*cos_theta);
        float phi= u(rng) * float(M_PI*2);
        Vector d= Vector(std::cos(phi) * sin_theta , cos_theta ,std::sin(phi) * sin_theta); 
        directions.push_back( d );
    }

    int ratioH = width / height;
    int ratioW = height / width; 
    // cree l'image resultat
    Image image(width, height); 

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
                    computePixelColorSources(sources, scene, pixel, color, infosIntersect, camera);
                    computePixelColorDome(directions,scene, pixel, infosIntersect, camera);
                } else {
                    pixel = pixel + White();
                }
            }
            pixel.a = 1;
            image(px, py)= Color(pixel / NB_ECHANTILLONS, 1);
        }
    }
    write_image(image, "image.png");
}

//--------------------------------------------------------main--------------------------------------------------------------

//! Couleur dome = White

int main()
{
    //camera
    Position camera;
    camera.o = Point(0, 0, 0);

    //Sources
    std::vector<Source> sources; 

    //Sources de lumière : panneau
    Point origine = Point(-0.5, -0.5, 0); 
    Vector axe_u = Vector(1, 0, 0); 
    Vector axe_v = Vector(0, 1, 0); 
    for(int i= 0; i < 5; i++) 
    for(int j= 0; j < 5; j++) {
        Source s;
        s.color = Color(1,1,0,1)/25;
        s.color.a = 1;
        float b= float(i) / float(5); 
        float c= float(j) / float(5);
        s.o = origine + b*axe_u + c*axe_v; // position du point dans la grille
        sources.push_back( s ); 
    }

    // Source sourcePonctuelle;
    // sourcePonctuelle.color = White() * 0.6;
    // sourcePonctuelle.color.a = 1;
    // sourcePonctuelle.o = Point(0, 0, 0);
    // sources.push_back( sourcePonctuelle );

    // sphere1
    Point c = Point(0, 0, -2);
    float r = 0.75;
    Sphere s;
    s.c = c;
    s.r = r;
    s.color = Red();
    Objet o1; 
    o1.id = 1;
    o1.s = &s;
    o1.p = NULL;
    o1.panneau = NULL;

    // sphere2 
    Point c2 = Point(1, 1, -5);
    float r2 = 2;
    Sphere s2;
    s2.c = c2;
    s2.r = r2;
    s2.color = Blue();
    Objet o3;
    o3.id = 1;
    o3.s = &s2;
    o3.p = NULL;
    o3.panneau = NULL;

    //panneau blanc
    Point o= Point(-2, -1, -1);
    Vector u= Vector(1, 0, 0);
    Vector v= Vector(0, 1, -0.25);
    Panneau panneau;
    panneau.o = o;
    panneau.u = u;
    panneau.v = v;
    panneau.n = cross(u, v);
    panneau.color = White();
    Objet o4;
    o4.id = 2;
    o4.p = NULL;
    o4.s = NULL;
    o4.panneau = &panneau;

    // plan
    Point a= Point(0, -1, 0);
    Vector n= Vector(0, 1, 0);
    Plan p;
    p.a = a;
    p.n = n;
    p.color = Color(0.5,0.5,0.5,1);
    Objet o2;
    o2.id = 0;
    o2.p = &p;
    o2.s = NULL;
    o2.panneau = NULL;

    //creer la scene
    Scene scene;
    scene.objets.push_back(o1);
    scene.objets.push_back(o2);
    scene.objets.push_back(o3);
    scene.objets.push_back(o4);
    scene.nb_objets = scene.objets.size();

    //dimensions images 
    int width = 1024;
    int height = 512;

    // avecAntialiasingSansDome(scene, camera, sources, width, height);
    // avecAntialiasingAvecDome(scene, camera, width, height);
    avecAntialiasingEtAll(scene, camera, sources, width, height);

    return 0;
}